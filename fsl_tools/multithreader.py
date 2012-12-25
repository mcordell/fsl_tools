__author__ = 'Michael'
from  threading import Thread
from Queue import Queue
import time, argparse
from subprocess import Popen, PIPE
from datetime import datetime

def append_to_log(message, use_time_stamp=True):
    """
    Simple log file method
    """
    with open('./feat_file_log.txt','a') as log_file:
        if use_time_stamp:
            time_stamp=datetime.now().strftime('[%Y-%m-%d %H:%m]')
        else:
            time_stamp='-'
        log_file.write(time_stamp+" "+message)
    log_file.close()

def runner(queue):
    while True:
        fsf_location= queue.get()
        print fsf_location
        append_to_log('Open file name: ' + fsf_location+'\n')
        command=['feat',fsf_location]
        process_object=Popen(command, stdout=PIPE, stderr=PIPE)
        sout,serr=process_object.communicate()
        if not process_object.returncode:
            append_to_log('Finished Cleanly: '+fsf_location+'\n')
        else:
            append_to_log('ERROR:            '+fsf_location+'\n')
            for line in serr:
                append_to_log(line,use_time_stamp=False)
        queue.task_done()

def searcher(queue, file_id):
    """
    Method to search the queue textfile for new lines that were added while
    the multithreader is runing
    """
    while True:
        try:
            line=file_id.readline()
        except:
            line=None
        #if we found something push it back into the queue and start over
        if line:
            while line:
                stripped_item=line.strip('\n')
                queue.put(stripped_item)
                line=file_id.readline()
        else:
            time.sleep(2)


if __name__ == "__main__":
    #load configuration file
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--cores',default=2)
    parser.add_argument('-q', '--queue_file',default='featfiles.txt')
    args=parser.parse_args()
    number_of_threads=args.cores
    queue_file_path=args.queue_file

    #create queue
    queue=Queue()

    #open list of filenames and populate the queue with it
    try:
        file_list_id=open(queue_file_path,'r')
        string_array=file_list_id.readlines()
        for item in string_array:
            stripped_item=item.strip('\n')
            queue.put(stripped_item)
    except IOError:
        print "We are missing the queue file. Default is featfiles.txt"
        exit()

    #start the searcher thread
    s_worker = Thread(target=searcher, args=(queue,file_list_id,))
    s_worker.setDaemon(True)
    s_worker.start()

    #set up the runner threads
    for i in range(number_of_threads):
        worker = Thread(target=runner, args=(queue,))
        worker.setDaemon(True)
        worker.start()

    #main_loop
    while True:
        #wait for everything to finish
        queue.join()
        #check to make sure nothing is added to the text file while we are running
        line=file_list_id.readline()
        if line:
            #if we found something push it back into the queue and start over
            while line:
                queue.put(line)
                line=file_list_id.readline()
        else:
            file_list_id.close()
            break
