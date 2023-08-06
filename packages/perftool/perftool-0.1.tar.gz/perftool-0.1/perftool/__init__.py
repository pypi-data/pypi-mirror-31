from __future__ import print_function
import sys, os
import platform
from datetime import datetime
import argparse

#Custom modules

from execute.executer import ExecutionInfo,ExecutionHandler



#shutil.copyfile(from_file,to_file)
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", help="Command to Execute")
    parser.add_argument("--DEBUG",help="Set Log level",action="store_true")
    parser.add_argument("--report", help="Generate Reports",type=bool)
    parser.add_argument("--duration",help="Duration of the Execution, Default is 5 minutes",type=int)
    args = parser.parse_args()

    if args.DEBUG:
        log_level = "DEBUG"

    else:
        log_level = "INFO"

    if args.report:
        exe_info = ExecutionInfo(False,log_level)

    else:
        exe_info = ExecutionInfo(True,log_level)

    if args.duration:
        exe_info.duration = args.duration


    if args.command:
        exe_info.command = args.command
        execution = ExecutionHandler(exe_info)
        exe_info.end_time = datetime.now()
        exe_info.summary()

    else:
        print("No command given")
    
def interactive(command):
    log_level = "WARN"
    exe_info = ExecutionInfo(False,log_level)
    exe_info.command = command 
    execution = ExecutionHandler(exe_info)
    exe_info.end_time = datetime.now()
    exe_info.summary()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        while True:
            command = input(">>")
            if command == "break":
                break

            elif "clear" in command:
                os.system('cls' if os.name == 'nt' else 'clear')
            else:
                interactive(command)
    else:
        main()
    

    
