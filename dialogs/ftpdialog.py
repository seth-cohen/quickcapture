"""
Class representing the Dialog box and logic presented
to the user when transferring data from the cameras to
the PI and over FTP

Python version 3.6

@author    Seth Cohen <scohen@wayfair.com>
@copyright 2018 Wayfair LLC - All rights reserved

"""

import os
import PyQt5.QtWidgets as Qtw
import PyQt5.QtCore as Qtc
import PyQt5.QtGui as Qtg
import configparser as conf
import ftplib as ftp
import pathlib
import Crypto.Cipher.AES as AES
import base64
import gphoto2 as gp
import time
import subprocess
import io

import dialogs.ftpdialog_auto as ftpdialog_auto
import consts
import usbcontroller


# Helper for static variables
def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate


class FTPDialog(Qtw.QDialog, ftpdialog_auto.Ui_FTPDialog):
    """Implementation of Dialog box that handles processes related to transfering files

    Spawns threads to initiate copying images to the PI, zipping the images and then 
    transferring them to our servers

    Attributes:
        is_canceled (bool): Whether ot not we've canceled a pending thread or operation
        cameras ([Camera]): The cameras that are attached to the machine
        config (object): The applications configuration object
        image_associations ([ImageAssociation]): List of all image associations taken as part of scan session
        scan_details (dict of str: [ScanDetails]): Dictionary of scans key is name of scan and value list of scan details
            tuple where first index is number of series and second is a string of notes/description of scan 

    """
    def __init__(self, config, cameras, image_associations, scan_details, base_dir):
        super().__init__()
        self.setupUi(self)

        self.is_canceled = False
        self.cameras = cameras
        self.config = config
        self.image_associations = image_associations
        self.scan_details = scan_details
        self.base_dir = base_dir

        path = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(path, 'logo.png')
        self.logo.setPixmap(Qtg.QPixmap(logo_path).scaled(self.logo.width(), self.logo.height(), Qtc.Qt.KeepAspectRatio))

        if self.config is None:
            self.config = conf.ConfigParser()
            self.config.read('/home/pi/.wayscan.conf')
    
        ftp_settings = self.config['FTP']
        self.host.setText(ftp_settings.get('host',  consts.DEFAULT_FTP_HOST))
        self.username.setText(ftp_settings.get('username', ''))

        # progress bars for the file copy thread operation
        self.progress_bars = []
        self.progress_bars.append(self.progress_1)
        self.progress_bars.append(self.progress_2)
        self.progress_bars.append(self.progress_3)
        self.progress_bars.append(self.progress_4)

        # progress bars for the file ftp transfer thread operation
        self.ftp_progress_bars = {}
        self.ftp_progress_bars['WF1'] = self.ftp_progress_1
        self.ftp_progress_bars['WF2'] = self.ftp_progress_2
        self.ftp_progress_bars['WF3'] = self.ftp_progress_3
        self.ftp_progress_bars['WF4'] = self.ftp_progress_4
        
        # keeping track of data transfer speeds
        self.ftp_speeds = {}
        self.ftp_speeds['WF1'] = self.speed_1
        self.ftp_speeds['WF2'] = self.speed_2
        self.ftp_speeds['WF3'] = self.speed_3
        self.ftp_speeds['WF4'] = self.speed_4
        
        # are we looking at kbps or mbps
        self.ftp_speed_units = {}
        self.ftp_speed_units['WF1'] = self.speed_unit_1
        self.ftp_speed_units['WF2'] = self.speed_unit_2
        self.ftp_speed_units['WF3'] = self.speed_unit_3
        self.ftp_speed_units['WF4'] = self.speed_unit_4
        
        self.dialog_buttons.button(Qtw.QDialogButtonBox.Ok).setText('Start Transfer')
        self.existing_dir.clicked.connect(self.upload_existing_directory)
        
        self.copy_threads = {}
        self.ftp_threads = {}

    def upload_existing_directory(self):
        # ensure that the ethernet USB controller is on
        usbcontroller.turn_ethernet_on()
        options = Qtw.QFileDialog.Options()

        options |= Qtw.QFileDialog.ShowDirsOnly
        dir = Qtw.QFileDialog.getExistingDirectory(
            self,
            'Select Directory To Transfer or Cancel to copy camera files or go back and start new scan',
            str(pathlib.Path.home()),
            options
        )

        if dir:
            # wait up to 5 seconds for ethernet to attach
            self.update_log('Configuring Network')
            Qtw.QApplication.processEvents()

            start_time = time.time()
            while time.time() - start_time < 5:
                ethernet_state = subprocess.check_output('cat /sys/class/net/eth0/operstate', shell=True)
                if ethernet_state.decode('utf-8').strip() == 'up':
                    break
                time.sleep(0.2)

            # wait up to 10 seconds for connection to network
            # essentially try to ping google.com until it responds or
            # 5 seconds passed
            host = self.host.text()
            self.update_log('Looking for {}'.format(host))
            Qtw.QApplication.processEvents()

            start_time = time.time()
            while time.time() - start_time < 15:
                ping = subprocess.check_output('ping -qc 1 {} > /dev/null && echo ok || echo error'.format(host), shell=True)
                if ping.decode('utf-8').strip() == 'ok':
                    self.update_log('Host Found')
                    break
                else:
                    self.update_log('Connecting to {}...'.format(host))
                    Qtw.QApplication.processEvents()
                time.sleep(0.2)

            self.begin_ftp_transfer(dir)
        
    def update_log(self, text):
        self.status_log.append(text)

    def update_copy_progress(self, value, cam_num):
        self.progress_bars[cam_num].setValue(value)

    def update_ftp_progress(self, value, key):
        self.ftp_progress_bars[key].setValue(value)

    @Qtc.pyqtSlot(int)
    def handle_copy_thread_complete(self, thread_num):
        """Slot for the copy thread completion signal

        Responds to the signal emitted whemn the copy thread is completed or canceled

        """
        self.copy_threads[thread_num].quit()
        self.copy_threads[thread_num].wait()
        del self.copy_threads[thread_num]

        if len(self.copy_threads) == 0:
            if self.is_canceled:
                self.set_dialog_buttons_state(True)
            else:
                usbcontroller.turn_ethernet_on()
                # wait up to 5 seconds for ethernet to attach
                self.update_log('Configuring Network')
                Qtw.QApplication.processEvents()

                start_time = time.time()
                while time.time() - start_time < 5:
                    ethernet_state = subprocess.check_output('cat /sys/class/net/eth0/operstate', shell=True)
                    if ethernet_state.decode('utf-8').strip() == 'up':
                        break
                    time.sleep(0.2)

                # wait up to 10 seconds for connection to network
                # essentially try to ping google.com until it responds or
                # 5 seconds passed
                host = self.host.text()
                self.update_log('Looking for {}'.format(host))
                Qtw.QApplication.processEvents()

                start_time = time.time()
                while time.time() - start_time < 15:
                    ping = subprocess.check_output('ping -qc 1 {} > /dev/null && echo ok || echo error'.format(host), shell=True)
                    if ping.decode('utf-8').strip() == 'ok':
                        self.update_log('Host Found')
                        break
                    else:
                        self.update_log('Connecting to {}...'.format(host))
                        Qtw.QApplication.processEvents()
                    time.sleep(0.2)

                Qtw.QApplication.processEvents()
                self.begin_ftp_transfer()

    @Qtc.pyqtSlot(str, str)
    def handle_ftp_thread_complete(self, key, remote_path):
        """Slot for the ftp thread completion signal

        Responds to the signal emitted whemn the ftp thread is completed or canceled

        """
        self.ftp_threads[key].quit()
        self.ftp_threads[key].wait()
        del self.ftp_threads[key]

        if len(self.ftp_threads) == 0:
            if self.is_canceled:
                self.set_dialog_buttons_state(True)
            else:
                print('Upload marker')
                try:
                    conn = get_ftp_connection(self.config)
                    conn.storbinary(
                        'STOR {}'.format(os.path.join(remote_path, 'needs_sorting')),
                        io.BytesIO(b'true')
                    )
                except ftp.all_errors as e:
                    self.handle_ftp_error(str(e))
                    return
                except NoPasswordError as e:
                    self.handle_password_not_set()
                    return

                print('We are done ftp')
                Qtw.QMessageBox.about(
                    self,
                    'Transfer Complete',
                    'Data transfer is complete. The app will now close. To shoot additional scans open the app again'
                )
                Qtw.QApplication.quit()

    @Qtc.pyqtSlot(int, str)
    def handle_speed_update(self, value, key):
        """Slot to update the FTP transfer speed

        """
        speed = '0'
        if value > 1024:
            value /= 1024
            self.ftp_speed_units[key].setText('mbps')
            speed = '{:.2f}'.format(value)
        else:
            self.ftp_speed_units[key].setText('kbps')
            speed = str(value)
        
        self.ftp_speeds[key].setText(speed)
        

    @Qtc.pyqtSlot()
    def handle_password_not_set(self):
        Qtw.QMessageBox.critical(self, 'FTP Details', 'Please configure your FTP details')
        
    @Qtc.pyqtSlot(str)
    def handle_ftp_error(self, error_message):
        self.set_dialog_buttons_state(True)
        Qtw.QMessageBox.critical(self, 'FTP Error', error_message)

    def copy_files_local(self):
        """Starts the process of copying files over from the camera to the Pi

        """
        base_dir = self.get_base_dir()
        
        self.status_log.append('Creating directory {}'.format(base_dir))
        os.makedirs(base_dir, exist_ok=True)
        
        self.status_log.append('Begin copying files')
        for cam_num, camera in enumerate(self.cameras):
            if camera.camera is not None:
                files = camera.list_files()
                if len(files) == 0:
                    print('No files from latest scan on camera {}'.format(cam_num))
                    continue
                    
                print(files)
                thread = CopyThread(camera, files, base_dir)

                thread.log_update_signal.connect(self.update_log)
                thread.progress_update_signal.connect(self.update_copy_progress)
                thread.has_completed_signal.connect(self.handle_copy_thread_complete)

                thread.start()
                print('Thread started')
                self.copy_threads[cam_num] = thread

        if len(self.copy_threads) == 0:
            Qtw.QMessageBox.critical(self, 'No Images', 'There are no images from the current scan')
        else:
            ## generate the image association file
            #with open(os.path.join(base_dir, 'image_map.csv'), 'w+') as csv_file:
            #    # Header
            #    csv_file.write('File,Scan ID,Series Num,Camera Num,Image Type,Aperture,ISO,Shutter\n')
            #    for image in self.image_associations:
            #        csv_file.write(str(image))

            # generate the scan details text file
            #with open(os.path.join(base_dir, 'scan_details.csv'), 'w+') as csv_file:
            #    # Camera Header
            #    csv_file.write('Camera Details\nCam Position, Cam Model, Serial, Lens\n')
            #    for cam in self.cameras:
            #        csv_file.write('{},{},{},{}\n'.format(cam.position, cam.model, cam.serial_num, cam.lens))

            #    # Scan Header
            #    csv_file.write('\nScan Details\nScan ID,Number of Series,Scan Type,Object Type,Scan Notes,Scan Name,Generate 3D Model?\n')
            #    for scan_name, part_details_list in self.scan_details.items():
            #        num_parts = len(part_details_list)
            #        for i, details in enumerate(part_details_list):
            #            name_for_csv = scan_name
            #            if i > 0:
            #                name_for_csv += '-{}ofX'.format(i + 1) 
            #            csv_file.write('{},{}\n'.format(name_for_csv, str(details)))
            self.existing_dir.setEnabled(False)

    def begin_ftp_transfer(self, dir=None):
        base_dir = self.get_base_dir()
        if dir is not None:
            base_dir = dir

        # Create the base directory on the FTP server if it doesn't already exist_ok
        try:
            conn = get_ftp_connection(self.config)
        except ftp.all_errors as e:
            self.handle_ftp_error(str(e))
            return
        except NoPasswordError as e:
            self.handle_password_not_set()
            return

        # See if the directory already exists on the server, if not create it
        try:
           server_list = conn.nlst()
           server_dir = os.path.basename(base_dir)
           if server_dir not in server_list:
               print('create directory on server {}'.format(server_dir))
               conn.mkd(server_dir)
        except ftp.all_errors as e:
            self.handle_ftp_error(str(e))
            return

        # create files on server and spawn new thread to upload camera directories for all dirs
        for node in os.listdir(base_dir):
            local_node = os.path.join(base_dir, node)
            remote_path = os.path.join(server_dir, node)
            if os.path.isfile(local_node):
                print('copy file {}'.format(local_node))
                with open(local_node, 'rb') as file:
                    conn.storbinary('STOR {}'.format(remote_path), file)
            elif os.path.isdir(local_node):              
                thread = FTPDirectoryThread(local_node, remote_path, self.config)
                
                # Connect the signals and slots
                thread.progress_update_signal.connect(self.update_ftp_progress)
                thread.speed_update_signal.connect(self.handle_speed_update)
                thread.log_update_signal.connect(self.update_log)
                thread.password_not_set_signal.connect(self.handle_password_not_set)
                thread.ftp_error_signal.connect(self.handle_ftp_error)
                thread.has_completed_signal.connect(self.handle_ftp_thread_complete)

                thread.start()
                print('FTP thread started')
                self.ftp_threads[node] = thread
            
    def get_base_dir(self):
        """Get the base directory to copy files to (defaults to current date)

        Returns:
            str: The base directory that we want to transfer to the server

        """
        if self.base_dir == None:
            self.base_dir = os.path.join(str(pathlib.Path.home()), time.strftime('%Y%m%d'))

        return self.base_dir

    def has_running_threads(self):
        """Whether or not the thread has any running threads still attached

        Returns:
            bool: Whether or not any threads are still attached

        """
        return len(self.copy_threads) > 0 or len(self.ftp_threads) > 0

    def set_dialog_buttons_state(self, should_enable=True):
        """Sets the state and title of the dialog buttons

        Controls whether the dialog buttons respond to click events (should_enable == True) or not.
        Will also set text appropriately do indicate whether we are in a pausable or cancelable state.
        
        Args:
           should_enable (bool): Whether or not we want to enable the buttons (default True)

        """
        if should_enable:
            self.dialog_buttons.button(Qtw.QDialogButtonBox.Ok).setText('Resume Transfer')
            self.dialog_buttons.button(Qtw.QDialogButtonBox.Ok).setEnabled(True)
            self.dialog_buttons.button(Qtw.QDialogButtonBox.Cancel).setText('Cancel')
            self.dialog_buttons.button(Qtw.QDialogButtonBox.Cancel).setEnabled(True)
        else:
            self.dialog_buttons.button(Qtw.QDialogButtonBox.Ok).setEnabled(False)
            self.dialog_buttons.button(Qtw.QDialogButtonBox.Ok).setText('Resume Transfer')
            self.dialog_buttons.button(Qtw.QDialogButtonBox.Cancel).setText('Pause')
        
    def accept(self):
        """Begins the transfer of files.

        The entire process is kicked off with this method. Copying files over from the cameras and then
        once those are copmletely copied and FTP them over to our network

        """
        self.is_canceled = False
        # only if we don't already have threads running, just incase, disable failed us
        if len(self.copy_threads) == 0:
            self.set_dialog_buttons_state(False)
            self.copy_files_local()


    def reject(self):
        """Cancel button was pressed

        This will either stop any running threads, effectively pausing or cancelling them.
        If no threads are running then this will cancel and close the dialog

        """
        for k, thread in self.copy_threads.items():
            thread.is_canceled = True

        for k, thread in self.ftp_threads.items():
            thread.is_canceled = True

        self.is_canceled = True
        if not self.has_running_threads():
            self.done(1)
        else:
            self.dialog_buttons.button(Qtw.QDialogButtonBox.Cancel).setEnabled(False)
            
class CopyThread(Qtc.QThread):
    # these need to be class variables
    log_update_signal = Qtc.pyqtSignal(str)
    progress_update_signal = Qtc.pyqtSignal(int, int)
    has_completed_signal = Qtc.pyqtSignal(int)
    def __init__(self, camera, file_list, base_dir, parent=None):
        """Sets initial attribute values
        
        Args:
            camera ${2:arg2}
            file_list ${3:arg3}
            base_dir ${4:arg4}
            parent ${6:arg6} (default None)

        """

    def __init__(self, camera, file_list, base_dir, parent=None):
        super().__init__(parent)

        self.is_canceled = False
        self.camera = camera
        self.file_list = file_list
        self.base_dir = base_dir

    def run(self):
        """The workhorse of the thread class

        This method will copy all of the files from the camera into a subdirectory of
        self.base_dir. The directory housing the files will be of the form WF<cam_num+1>

        """
        file_count = len(self.file_list)
        self.log_update_signal.emit('Copy {} files for camera {}'.format(file_count, 1))
        
        for file_num, file in enumerate(self.file_list):
            if self.is_canceled == True:
                break
            
            info = self.camera.get_file_info(file)
            folder, name = os.path.split(file)

            self.log_update_signal.emit('File: {} copying size: {}'.format(name, info.file.size))

            cam_dir = os.path.join(self.base_dir,'WF{}'.format(self.camera.position + 1))
            os.makedirs(cam_dir, exist_ok=True)

            file_path = os.path.join(cam_dir, name)
            if not os.path.isfile(file_path):
                self.progress_update_signal.emit(100 * (file_num + 1) / file_count, self.camera.position)

                start = time.time()
                data = self.camera.camera.file_get(folder, name, gp.file.GP_FILE_TYPE_NORMAL).get_data_and_size()
                print('Time to get data {}'.format(time.time() - start))

                with open(os.path.join(cam_dir, name), 'wb+') as image_file:
                    start = time.time()
                    image_file.write(data)
                    print('Time to save file {}'.format(time.time() - start))
            else:
                self.log_update_signal.emit('File {} already exists. Skipping...'.format(name))
                print('File {} already exists. Skipping...'.format(name))

        # We finished of our our accord so we should update the progress_bar 
        if not self.is_canceled:
            self.progress_update_signal.emit(100, self.camera.position)

        self.has_completed_signal.emit(self.camera.position)

class FTPDirectoryThread(Qtc.QThread):
    """Class responsible for transferring a file or directory to the service

    Runs as a thread giving us the ability to cancel the thread at any point
    Additionally, this thread will try to resume for where any previous attempts have left off 
    by tracking the bytes that have been successfully transfered already

    Attributes:
        is_canceled (bool): Whether or not to exit the thread
        file_path (str): The file that we want to transfer
        config (object): The application configuration object
        bytes_transferred (int): Number of bytes of this file already received by server
        total_bytes (int): size in bytes of the file to transfer
        conn (object): The FTP connection Object
        append_if_exists (bool): When true will start the transfer at offset of size of file on server if exists

   """ 
    # Signals for the main thread to bind to a slot to get updates from the thread
    # Yes, these need to be class variables or else PyQt5 will bind them to the class by default.
    log_update_signal = Qtc.pyqtSignal(str)
    progress_update_signal = Qtc.pyqtSignal(int, str)
    speed_update_signal = Qtc.pyqtSignal(int, str)
    password_not_set_signal = Qtc.pyqtSignal()
    ftp_error_signal = Qtc.pyqtSignal(str)
    has_completed_signal = Qtc.pyqtSignal(str, str)
    
    def __init__(self, local_directory, remote_path, config, append_if_exists=False, parent=None):
        """Constuctor for the thread, just initializes serveral attributes
        
        Args:
            file_path (str): The path to the file that we want to send to server
            config (ConfigParser): The configuration for the application
            parent (QObject): Parent PyQt5 object that this may belong to (default None)

        """
        super().__init__(parent)

        self.is_canceled = False
        self.local_directory = local_directory
        self.remote_path = remote_path
        self.config = config
        self.server_parent_dir, self.server_basename = os.path.split(self.remote_path)
        self.num_files_tranfered = 0
        self.bytes_transferred = 0
        self.bytes_last_update = 0
        self.start_time = None
        self.append_if_exists = append_if_exists

    def run(self):
        """The workhorse of the thread class

        This method will continue looping through all of the files in the base_dir attributes
        and create an archive of the same name with the `zip` extension

        """
        try:
            self.log_update_signal.emit('Creating FTP Connection')
            self.conn = get_ftp_connection(self.config)
        except ftp.all_errors as e:
            self.ftp_error_signal.emit(str(e))
            return
        except NoPasswordError as e:
            self.password_not_set_signal.emit()
            return
            

        # create the directory on the server if it doesn't exists
        try:
            server_list = self.conn.nlst(self.server_parent_dir)
            if self.server_basename not in server_list:
                print('create directory on server: {}'.format(self.remote_path))
                self.log_update_signal.emit('create directory on server: {}'.format(self.remote_path))
                self.conn.mkd(self.remote_path)
        except ftp.all_errors as e:
            self.handle_ftp_error(str(e))
            return

        # get the total file count to keep progress
        self.total_files = sum([len(files) for r, d, files in os.walk(self.local_directory)])

        # we will want to know list of all the files in the server directory so we don't send twice 
        try:
            server_files = {name: data for name, data in list(self.conn.mlsd(self.remote_path))}
        except ftp.all_errors as e:
            self.handle_ftp_error(str(e))
            return
        
        # create files on server and spawn new thread to upload camera directories for all dirs
        for node in sorted(os.listdir(self.local_directory)):
            local_node = os.path.join(self.local_directory, node)
            remote_path = os.path.join(self.remote_path, node)
            rest = None
            if os.path.isfile(local_node):
                file_already_present = False
                # check to see if the file exists
                if node not in server_files:
                    print('copy file {}'.format(local_node))
                    self.log_update_signal.emit('copy file {}'.format(local_node))
                else:
                    local_size = os.path.getsize(local_node)
                    server_size = int(server_files[node]['size'])
                    print('Server has {} of {} bytes...'.format(server_size, local_size))
                    self.log_update_signal.emit('Server has {} of {} bytes...'.format(server_size, local_size))
                    if local_size > server_size:
                        # rest is the byte offset to start transferring from
                        rest = server_size
                    else:
                        print('Skipping {}...'.format(remote_path))
                        self.log_update_signal.emit('Skipping {}...'.format(remote_path))
                        file_already_present = True

                if not file_already_present:
                    with open(local_node, 'rb') as file:
                        try:
                            # only send what the server doesn't already have... so we need to move the read cursor
                            if rest is not None:
                                file.seek(rest)
                            self.conn.storbinary('STOR {}'.format(remote_path), file, callback=self.handle_transfer_block_complete, rest=rest)
                        except ftp.all_errors as e:
                            self.ftp_error_signal.emit(str(e))
                            break;
                    
            self.num_files_tranfered += 1
            self.progress_update_signal.emit(100 * self.num_files_tranfered / self.total_files, self.server_basename)


        # We finished of our our accord so we should update the progress_bar 
        if not self.is_canceled:
            self.progress_update_signal.emit(100, self.server_basename)

        self.has_completed_signal.emit(self.server_basename, self.server_parent_dir)
        self.speed_update_signal.emit(0, self.server_basename)
        self.conn.quit()
        self.conn = None
                
    def handle_transfer_block_complete(self, block):
        """The callback for ftplib to call when a block of data has been received by server

        """
        self.bytes_transferred += len(block)
        
        if self.start_time is not None:
            # Update transfer speed if 500 milliseconds has passed
            # @TODO calculate time left for upload
            elapsed = time.time() - self.start_time
            if elapsed > 0.5:
                bytes_transferred = self.bytes_transferred - self.bytes_last_update
                speed = bytes_transferred / elapsed 
                self.speed_update_signal.emit(int(speed / 1024), self.server_basename)
                
                self.bytes_last_update = self.bytes_transferred
                self.start_time = time.time()
        else:
            self.bytes_last_update = self.bytes_transferred
            self.start_time = time.time()
                
        if self.is_canceled:
            print('Cancelling FTP')
            self.conn.quit()
            self.conn = None

            self.quit()
            self.wait()

def get_ftp_connection(config):
    ftp_settings = config['FTP']
    host = ftp_settings.get('host', consts.DEFAULT_FTP_HOST)
    username = ftp_settings.get('username', '')

    # decrypt the hashed password
    hash = base64.b64decode(ftp_settings.get('h', ''))
    tag = base64.b64decode(ftp_settings.get('t', ''))
    nonce = base64.b64decode(ftp_settings.get('n', ''))
    key = base64.b64decode(ftp_settings.get('k', ''))
    if len(hash) > 0 and len(tag) > 0 and len(nonce) > 0 and len(key) > 0:
        cipher = AES.new(key, AES.MODE_EAX, nonce)
        pw = cipher.decrypt_and_verify(hash, tag).decode('utf-8')
    else:
        raise NoPasswordError()
    return ftp.FTP(host, user=username, passwd=pw)

class NoPasswordError(Exception):
    def __init__(self):
        Exception.__init__(self, 'No password set')
