import os
# import psutil
import glob
import time
import datetime
import logging
import platform
import subprocess


###################
# CONSTANT VALUE
###################
INTERVAL_TIME = 3 # sec


###################
# set logger
###################
filename = os.path.basename(__file__).replace('.py', '')
logfile_date = datetime.datetime.now().strftime('%Y_%m_%d')
log_file_path = f'./watchdog_log/{logfile_date}_{filename}.log'

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
logger = logging.getLogger(__name__)
handler = logging.FileHandler(log_file_path)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

logger.info('**************** start ***************')
    

# def get_process_info(pid):
#     try:
#         process = psutil.Process(pid)
#         cpu_usage = process.cpu_percent(interval=1)  # Usage rate of CPU/sec
#         memory_info = process.memory_info()  # Usage of Memory
#         num_threads = process.num_threads()  # Num of threads

#         logger.debug({"Process ID": f"{pid}", "CPU Usage": f"{cpu_usage}%", "Number of Threads": f"{num_threads}"})
#         logger.debug({"Memory Usage(RSS)": f"{memory_info.rss / (1024 * 1024):.2f} MB", "Memory Usage(VMS)": f"{memory_info.vms / (1024 * 1024):.2f} MB"})

#     except psutil.NoSuchProcess:
#         logger.debug(f"No process found with PID: {pid}")



class WatchDog():
    '''This is Watch dog Class
    arg1: The folder path that you want to be watching.
    arg2: An extention what you want to be watching(It is OK that there is no arg2).
    '''
    def __init__(self, path, extention=None):
        path = path.replace(os.path.sep, '/')
        if path[-1] != '/':
            self.path += '/'
        else:
            self.path = path


        if extention is not None:
            if extention.startswith('.'):
                self.ext = extention 
            else:
                self.ext = '*.' + extention
        else:
            self.ext = '*'

        self.watching_path = f'{self.path}{self.ext}'
        # print(self.watching_path)
        
        # 初期状態を記録
        self.temp_files_list = glob.glob(self.watching_path)
        self.temp_files_list = [x.replace(os.path.sep, '/') for x in self.temp_files_list]
        self.temp_num_file = 0
        self.temp_update_times = {}

        for file in self.temp_files_list:
            last_s_time = datetime.datetime.fromtimestamp(os.path.getmtime(file))
            self.temp_update_times[file] = last_s_time
        
        self.temp_access_times = {}
        for file in self.temp_files_list:
            last_a_time = datetime.datetime.fromtimestamp(os.path.getatime(file))
            self.temp_access_times[file] = last_a_time

        logger.debug({
            'class': 'WatchDog',
            'action': 'establish instance',
            'args': f'path: {self.path} / ext: {self.ext}',
        })


    def access_check(self, files: list):
        '''return pathes of files that are not accessed
        '''
        pf = platform.system()
        non_access_files = []

        if pf == 'Windows':
            for file in files:
                try:
                    with open(file, 'r+'):
                        non_access_files.append(file)
                except IOError as e:
                    logger.debug({
                        'aciton': 'access_check',
                        'status': f'error: {e}',
                    })
            return non_access_files
        
        elif (pf == 'Darwin') or (pf == 'Linux'):
            # 未検証
            for file in files:
                try:
                    # lsof コマンドを実行し、出力を取得
                    result = subprocess.run(['lsof', file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    if result.stdout:
                        logger.debug({
                            'files status': 'accessed',
                            'file path': file,
                        })
                    else:
                        non_access_files.append(file)

                except Exception as e:
                    logger.error({
                        'action': 'access check',
                        'status': f'error: {e}',
                    })
            return non_access_files
        
        else:
            logger.info({
                'action': 'access check',
                'status': 'unknown OS',
                'return': 'return all pathes',
            })
            return files

            


    def watch_file_existance(self):
        '''When the presence of the files is confirmed, 
        it outputs True and a list of the files as the return value. 
        It is assumed that these files will be deleted or moved to another folder after processing.
        '''
        watching_files = glob.glob(self.watching_path)
        watching_files = [x.replace(os.path.sep, '/') for x in watching_files]
        watching_files = self.access_check(watching_files)

        ##############################
        # add reglar expression, if you need.
        ##############################

        # if pid is not None:
        #     get_process_info(pid)

        if len(watching_files) == 0:
            flag = False
        else:
            flag = True
            logger.debug({
                'action': 'watching file existance',
                'status': 'added new files',
                'num of files': len(watching_files),
            })

        return flag, watching_files
    
        
    def watch_add_new_files(self, return_past_files=False):
        '''When the presence of "New" files is confirmed,
        it outputs True and a list of "New" files as the return value.
        But files were removed or moved from this folder, it output nothing
        
        If a file was created with a name that existed in tha past,
        ** if return_past_files=False(default)
        it will not output False & None.
        ** if return_past_files=True
        it will output True & file list.

        It is assumed that these files are remain this folder after processing.
        '''
        watching_files = glob.glob(self.watching_path)
        watching_files = [x.replace(os.path.sep, '/') for x in watching_files]
        watching_files = self.access_check(watching_files)

        ##############################
        # add reglar expression, if you need.
        ##############################

        new_files = []

        for watching_file in watching_files:
            if watching_file not in self.temp_files_list:
                new_files.append(watching_file)

        if return_past_files:
            self.temp_files_list = watching_files # temp fileの更新
        else:
            self.temp_files_list += watching_files
            self.temp_files_list = list(set(self.temp_files_list))

        # if pid is not None:
        #     get_process_info(pid)

        if len(new_files) == 0:
            flag = False
            new_files = None
        else:
            flag = True
            logger.debug({
                'action': 'watch_add_new_files',
                'status': 'files were added',
                'return a file exist at past': return_past_files,
                'num of files': len(watching_files),
            })
        
        return flag, new_files
    
    
    def watch_removed_files(self):
        '''If it is confirmed that files that existed in this folder have been removed or moved,
        it output True and list of removed files.
        
        '''
        watching_files = glob.glob(self.watching_path)
        watching_files = [x.replace(os.path.sep, '/') for x in watching_files]

        ##############################
        # 必要ならここに正規表現を入れる
        ##############################

        remove_files = []

        for temp_file in self.temp_files_list:
            if temp_file not in watching_files:
                remove_files.append(temp_file)

        self.temp_files_list = watching_files # 更新

        # if pid is not None:
        #     get_process_info(pid)

        if len(remove_files) == 0:
            flag = False
            remove_files = None
        else:
            flag = True
            logger.debug({
                'action': 'watch removed files',
                'status': 'files were removed',
                'num of files': len(watching_files),
            })

        return flag, remove_files
    

    def watch_update_time(self, return_past_files=False):
        '''If it is confirmed that files have been updated,
        it output True and updated files list.

        If files have been removed and added again with same name,
        ** If return_past_files is True,
        If a file was create with the file name that have been exist at past,
        it output "True & a file list with this file".
        ** If return_past_files is False,
        If a file was create with the file name that have been exist at past,
        it output "False & a file list without this file".

        '''
        watching_files = glob.glob(self.watching_path)
        watching_files = [x.replace(os.path.sep, '/') for x in watching_files]
        watching_files = self.access_check(watching_files)

        update_files = []

        # 新しくファイルが保存されたり、ファイルがなくなったりしたときの処理を追加する
        
        for file in watching_files:
            s_time = datetime.datetime.fromtimestamp(os.path.getmtime(file))

            if file not in self.temp_update_times.keys() or self.temp_update_times[file] < s_time:
                update_files.append(file)
                self.temp_update_times[file] = s_time

        # exist_at_pastがTrueの場合は過去に存在していたファイルも返り値として返す
        # つまり、削除されたファイルのtemp_update_times時間を削除
        if return_past_files:
            temp_update_times_to_delete = []
            for temp_file in self.temp_update_times.keys():
                if temp_file not in watching_files:
                    temp_update_times_to_delete.append(temp_file)
            for del_file in temp_update_times_to_delete:
                del self.temp_update_times[del_file]

        
        # if pid is not None:
        #     get_process_info(pid)

        if len(update_files) == 0:
            flag = False
            update_files = None
        else:
            flag = True
            logger.debug({
                'action': 'watch update time',
                'status': 'files were updated',
                'num of files': len(watching_files),
            })
        
        return flag, update_files
    

    #####################################################################
    ####################### ここまで ###########################
    #####################################################################
      

if __name__ == "__main__":
    ###################
    # constant
    ###################
    # テスト用
    path1 = './watch_folder1/'
    path2 = './watch_folder2/'
    path3 = './watch_folder3/'


    # current_pid = os.getpid()  # 現在のプロセスIDを取得

    watchdog1 = WatchDog(path1)
    watchdog2 = WatchDog(path2)
    watchdog3 = WatchDog(path3)


    while True:
        flag1, watching_files1 = watchdog1.watch_add_new_files(return_past_files=True)
        flag2, watching_files2 = watchdog2.watch_add_new_files(return_past_files=True)
        flag3, watching_files3 = watchdog3.watch_add_new_files(return_past_files=True)

        flag2_3 = sum([flag2, flag3]) # 二か所のフォルダを監視する場合


        if flag1: # 一か所のフォルダを監視する場合
            print(f'************ start main process {os.path.basename(path1)} ************')
            # 以下は実行例
            command1 = 'python aaa.py'
            result_1 = subprocess.run(command1, shell=True, capture_output=True, text=True)
            error_1 = result_1.stderr
            logger.error({
                'action': command2,
                'error': error_1,
            })

        elif flag2_3: # 二か所のフォルダを監視する場合
            print(f'************ start main process {os.path.basename(path2)} / {os.path.basename(path3)} ************')
            # 以下は実行例
            command2 = 'python bbb.py'
            result_2 = subprocess.run(command2, shell=True, capture_output=True, text=True)
            error_2 = result_2.stderr
            logger.error({
                'action': command2,
                'error': error_2,
            })
        else:
            pass

        time.sleep(INTERVAL_TIME)

