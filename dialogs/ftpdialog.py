import os
import PyQt5.QtWidgets as Qtw
import PyQt5.QtCore as Qtc
import PyQt5.QtGui as Qtg
import configparser as conf
import ftplib as ftp
import zipfile as zip
import pathlib
import Crypto.Cipher.AES as AES
import base64
import gphoto2 as gp
import time
import threading

import dialogs.ftpdialog_auto as ftpdialog_auto
import consts


# Helper for static variables
def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
            print('Setting {} on {}'.format(k, func))
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

    """
    def __init__(self, config, cameras):
        super().__init__()
        self.setupUi(self)

        self.is_canceled = False
        self.cameras = cameras
        self.config = config

        path = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(path, 'logo.png')
        self.logo.setPixmap(Qtg.QPixmap(logo_path).scaled(self.logo.width(), self.logo.height(), Qtc.Qt.KeepAspectRatio))

        if self.config is None:
            self.config = conf.ConfigParser()
            self.config.read('/home/pi/.quickcapture.conf')
    
        ftp_settings = self.config['FTP']
        self.host.setText(ftp_settings.get('host',  consts.DEFAULT_FTP_HOST))
        self.username.setText(ftp_settings.get('username', ''))

        self.progress_bars = []
        self.progress_bars.append(self.progress_1)
        self.progress_bars.append(self.progress_2)
        self.progress_bars.append(self.progress_3)
        self.progress_bars.append(self.progress_4)

        self.dialog_buttons.button(Qtw.QDialogButtonBox.Ok).setText('Start Transfer')
        
        self.copy_threads = {}
        self.zip_thread = None
        self.ftp_thread = None
        
    def update_log(self, text):
        self.status_log.append(text)

    def update_copy_progress(self, value, cam_num):
        self.progress_bars[cam_num].setValue(value)

    def update_zip_progress(self, value):
        print('Setting zip progress')
        self.zip_progress.setValue(value)
        
    def update_ftp_progress(self, value):
        self.ftp_progress.setValue(value)

    @Qtc.pyqtSlot(int)
    def handle_copy_thread_complete(self, thread_num):
        self.copy_threads[thread_num].quit()
        self.copy_threads[thread_num].wait()
        del self.copy_threads[thread_num]

        if len(self.copy_threads) == 0:
            if self.is_canceled:
                self.set_dialog_buttons_state(True)
            else:
               self.zip_thread = ZipThread(self.get_base_dir())
               
               self.zip_thread.log_update_signal.connect(self.update_log)
               self.zip_thread.progress_update_signal.connect(self.update_zip_progress)
               self.zip_thread.finished.connect(self.handle_zip_thread_complete)

               self.zip_thread.start()

    @Qtc.pyqtSlot()
    def handle_zip_thread_complete(self):
        """Slot for the zip thread completion signal

        Responds to the signal emitted whemn the zip thread is completed or canceled

        """
        print('Finished Zip Thread')
        self.zip_thread = None
        if self.is_canceled:
            self.set_dialog_buttons_state(True)
        else:
            self.status_log.append('Starting FTP thread...')
            self.ftp_thread = FTPThread(self.get_base_dir() + '.zip', self.config, True)

            self.ftp_thread.log_update_signal.connect(self.update_log)
            self.ftp_thread.progress_update_signal.connect(self.update_ftp_progress)
            self.ftp_thread.speed_update_signal.connect(self.handle_speed_update)
            self.ftp_thread.finished.connect(self.handle_ftp_thread_complete)

            self.ftp_thread.start()
            
    @Qtc.pyqtSlot()
    def handle_ftp_thread_complete(self):
        """Slot for the ftp thread completion signal

        Responds to the signal emitted whemn the ftp thread is completed or canceled

        """
        self.ftp_thread = None
        if self.is_canceled:
            self.set_dialog_buttons_state(True)
        else:
            print('We are done ftp')

    @Qtc.pyqtSlot(int)
    def handle_speed_update(self, value):
        """Slot to update the FTP transfer speed

        """
        self.speed.setText(str(value))
        

    def copy_files_local(self):
        """Starts the process of copying files over from the camera to the Pi

        """
        base_dir = self.get_base_dir()
        
        self.status_log.append('Creating file {}'.format(base_dir))
        os.makedirs(base_dir, exist_ok=True)
        
        self.status_log.append('Begin copying files')
        for cam_num, camera in enumerate(self.cameras):
            if camera.camera is not None:
                files = camera.list_files('/')
                thread = CopyThread(camera, files, base_dir)

                thread.log_update_signal.connect(self.update_log)
                thread.progress_update_signal.connect(self.update_copy_progress)
                thread.has_completed_signal.connect(self.handle_copy_thread_complete)

                thread.start()
                print('Thread started')
                self.copy_threads[cam_num] = thread

    def get_base_dir(self):
        """Get the base directory to copy files to (defaults to current date)

        Returns:
            str: The base directory that we want to transfer to the server

        """
        return os.path.join(str(pathlib.Path.home()), time.strftime('%Y%m%d'))

    def has_running_threads(self):
        """Whether or not the thread has any running threads still attached

        Returns:
            bool: Whether or not any threads are still attached

        """
        return len(self.copy_threads) > 0 or self.zip_thread is not None or self.ftp_thread is not None

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
        once those are copmletely copied, will zip them, and finally FTP them over to our network

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

        if self.zip_thread is not None:
            self.zip_thread.is_canceled = True

        if self.ftp_thread is not None:
            self.ftp_thread.is_canceled = True

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
    def __init__(self, camera, file_list, base_dir, progress_bar=None, parent=None):
        """Sets initial attribute values
        
        Args:
            camera ${2:arg2}
            file_list ${3:arg3}
            base_dir ${4:arg4}
            progress_bar ${5:arg5} (default None)
            parent ${6:arg6} (default None)

        """
        

    def __init__(self, camera, file_list, base_dir, progress_bar=None, parent=None):
        super().__init__(parent)

        self.is_canceled = False
        self.camera = camera
        self.file_list = file_list
        self.progress_bar = progress_bar
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

            self.log_update_signal.emit('File: {} downloading size: {}'.format(name, info.file.size))

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

class ZipThread(Qtc.QThread):
    """Class responsible for zipping all of the contents of a directory

    Runs as a thread giving us the ability to cancel the thread at any point
    Additionally, this thread will try to resume for where any previous attempts have left off

    Attributes:/Download
        is_canceled (bool): Whether or not to exit the thread
        base_dir (str): The directory that we want to archive

   """ 
    log_update_signal = Qtc.pyqtSignal(str)
    progress_update_signal = Qtc.pyqtSignal(int)

    def __init__(self, base_dir, parent=None):
        """Constuctor for the thread, just initializes serveral attributes
        
        Args:
            parent (QObject): Parent PyQt5 object that this may belong to (default None)

        """
        super().__init__(parent)

        self.is_canceled = False
        self.base_dir = base_dir

    def run(self):
        """The workhorse of the thread class

        This method will continue looping through all of the files in the base_dir attributes
        and create an archive of the same name with the `zip` extension

        """
        base_dir = self.base_dir
        self.zipfile = base_dir + '.zip'

        # If we are continuing a previously canceled zip, we shouldn't
        # have to re-write existing files
        zipped_files_list = []
        if os.path.isfile(self.zipfile):
            with zip.ZipFile(self.zipfile, 'r') as zipped:
                zipped_files_list.extend(zipped.namelist())
        
        with zip.ZipFile(self.zipfile, 'a', compression=zip.ZIP_DEFLATED) as zipit:
            # quickly recurse to get total count of files to zip so
            # so we can update progress bar
            total_files = sum([len(files) for r, d, files in os.walk(base_dir)])
            cur_file_num = 0

            # os.walk built on listdir which doesn't gaurantee any order so let's sort the files and dirs
            for base, dirs, files in os.walk(base_dir):
                dirs.sort()
                for file in sorted(files):
                    # Main thread canceled us :(
                    if self.is_canceled:
                        break

                    # os.walk returns `base` as the full path to get the the current directory it is traversing
                    # this would lead to terrible archive structure as files within the zip would be nested deep
                    # in the directory tree (like `zip_name/home/pi/Documents/YYYYMMDD/WF1/IMGXXXX.cr2`), yuck
                    file_name = os.path.join(os.path.relpath(base, os.path.dirname(self.base_dir)), file)
                    if not file_name in zipped_files_list:
                        start = time.time()
                        zipit.write(os.path.join(base, file), file_name)
                        self.log_update_signal.emit('Zipping file: {}'.format(file))
                        print('Time to Zip file {}'.format(time.time() - start))
                    else:
                        # Don't rewrite the files that have already been written before a pause or cancel and resume
                        self.log_update_signal.emit('File {} already zipped. Skipping...'.format(file_name))
                        print('File {} already zipped. Skipping...'.format(file_name))
                        
                        
                    cur_file_num += 1
                    self.progress_update_signal.emit(100 * (cur_file_num + 1) / total_files)

        # We finished of our our accord so we should update the progress_bar 
        if not self.is_canceled:
            self.progress_update_signal.emit(100)
                
class FTPThread(Qtc.QThread):
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
    log_update_signal = Qtc.pyqtSignal(str)
    progress_update_signal = Qtc.pyqtSignal(int)
    speed_update_signal = Qtc.pyqtSignal(int)

    def __init__(self, file_path, config, append_if_exists=False, parent=None):
        """Constuctor for the thread, just initializes serveral attributes
        
        Args:
            file_path (str): The path to the file that we want to send to server
            parent (QObject): Parent PyQt5 object that this may belong to (default None)

        """
        super().__init__(parent)

        self.is_canceled = False
        self.file_path = file_path
        self.config = config
        self.bytes_transferred = 0
        self.total_bytes = 0
        self.conn = None
        self.append_if_exists = append_if_exists

    def run(self):
        """The workhorse of the thread class

        This method will continue looping through all of the files in the base_dir attributes
        and create an archive of the same name with the `zip` extension

        """
        print('Beginning FTP transfer')
        ftp_settings = self.config['FTP']
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

        try:
            self.conn = ftp.FTP(host, user=username, passwd=pw)
            # Get file size
            self.total_bytes = os.path.getsize(self.file_path)
            self.log_update_signal.emit('Connected to {}'.format(host))
            self.log_update_signal.emit('File Size: {} bytes. File Name: {}'.format(self.total_bytes, self.file_path))

            server_file = os.path.basename(self.file_path)
            if self.append_if_exists:
                size_on_server = self.conn.size(server_file)
                if size_on_server is not None:
                    self.log_update_signal.emit('Server has {} bytes already... skipping'.format(size_on_server))
                    self.bytes_transferred = size_on_server

            # Open file for transfer
            file = open(self.file_path, 'rb')
            self.conn.storbinary('STOR {}'.format(server_file), file, callback=self.handle_transfer_block_complete, rest=self.bytes_transferred)
        except Exception as e:
            print(str(e))
                
    @static_vars(start_time=None, bytes_last_update=0)
    def handle_transfer_block_complete(self, block):
        self.bytes_transferred += len(block)
        self.progress_update_signal.emit(100 * self.bytes_transferred / self.total_bytes)
        
        if FTPThread.handle_transfer_block_complete.start_time is not None:
            # Update if 300 milliseconds has passed
            elapsed = time.time() - FTPThread.handle_transfer_block_complete.start_time
            if elapsed > 0.3:
                bytes_transferred = self.bytes_transferred - FTPThread.handle_transfer_block_complete.bytes_last_update
                speed = bytes_transferred / elapsed 
                self.speed_update_signal.emit(int(speed / 1024))
                
                FTPThread.handle_transfer_block_complete.bytes_last_update = self.bytes_transferred
                FTPThread.handle_transfer_block_complete.start_time = time.time()
        else:
            FTPThread.handle_transfer_block_complete.bytes_last_update = self.bytes_transferred
            FTPThread.handle_transfer_block_complete.start_time = time.time()
                
        if self.is_canceled:
            print('Cancelling FTP')
            self.conn.quit()
            self.conn = None

            self.quit()
            self.wait()


