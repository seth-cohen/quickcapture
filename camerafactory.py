import gphoto2 as gp


class CameraFactory():
    __instance = None

    def get_instance():
        if CameraFactory.__instance == None:
            CameraFactory()
        
        return CameraFactory.__instance

    def __init__(self):
        if CameraFactory.__instance != None:
            raise Exception('Do not call CameraFactory() directly. Use static get_instance')
        else:
            self.cameras = {}
            CameraFactory.__instance = self

    def get_cameras(self):
        if len(self.cameras) == 0:
            camera_list = []
            for name, addr in gp.check_result(gp.gp_camera_autodetect()):
                camera_list.append((name, addr))

            if len(camera_list) == 0:
                print('No Cameras Detected')
                QMessageBox.about(
                    self,
                    'Error Detecting Cameras',
                    'No cameras were detected. Confirm that 4 cameras are attached'
                )

            for index, (name, addr) in enumerate(camera_list):
                print('{:d}: {:s} {:s}'.format(index, addr, name))
                context = gp.Context()
                camera = gp.Camera()

                port_info_list = gp.PortInfoList()
                port_info_list.load()
                idx = port_info_list.lookup_path(addr)
                camera.set_port_info(port_info_list[idx])
                camera.init(context)

                camera_config = camera.get_config(context)
                serial = camera_config.get_child_by_name('eosserialnumber') 
                self.cameras[serial.get_value()] = (camera, {'port_index': idx})

        return self.cameras

    def get_camera_serials(self):
        return sorted(self.get_cameras().keys())

    def get_camera(self, serial_num):
        print('Getting serial {}'.format(serial_num))
        if serial_num in self.get_cameras():
             return self.get_cameras()[serial_num][0]
              
        print('Not Found') 
        return None
    
    def __del__(self):
        for k, v in self.cameras.items():
            print('exiting camera')
            v[0].exit(context)
