__author__ = 'Michael'
from  threading import Thread
from Queue import Queue
import time, argparse
from subprocess import Popen, PIPE

#number of concurrent threads
number_of_threads=2

def Runner(queue):
    while True:
        fsf_location= queue.get()
        print fsf_location

        file_id=open('./feat_file_log.txt','a')
        file_id.write('Open file name: ' + fsf_location+'\n')
        file_id.close()
        file_id=open('./feat_file_log.txt','a')
        command=['feat',fsf_location]
        process_object=Popen(command, stdout=PIPE, stderr=PIPE)
        sout,serr=process_object.communicate()
        if process_object.returncode == 0:
            file_id.write('Finished Cleanly: '+fsf_location+'\n')
        else:
            file_id.write('ERROR:            '+fsf_location+'\n')
            for line in serr:
                file_id.write(line)
        queue.task_done()

def searcher(queue, file_id):
    """

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
    parser.add_argument('-c', '--cores')
    args=parser.parse_args()
    number_of_threads=args.cores
    if number_of_threads is None:
        number_of_threads=2
    else:
        number_of_threads=int(number_of_threads)

    #create queue
    queue=Queue()

    #open list of filenames and populate the queue with it
    try:
        file_list_id=open('./featfiles.txt','r')
        string_array=file_list_id.readlines()
        for item in string_array:
            stripped_item=item.strip('\n')
            queue.put(stripped_item)
    except:
        print "No featfiles.txt here"
        exit()



    #start the searcher thread
    s_worker = Thread(target=searcher, args=(queue,file_list_id,))
    s_worker.setDaemon(True)
    s_worker.start()

    #set up the runner threads
    for i in range(number_of_threads):
        worker = Thread(target=Runner, args=(queue,))
        worker.setDaemon(True)
        worker.start()

    #main_loop
    while True:
        #wait for everything to finish
        queue.join()
        #check to make sure nothing is added to the text file while we are rsyncing
        line=file_list_id.readline()
        if line:
            #if we found something push it back into the queue and start over
            while line:
                queue.put(line)
                line=file_list_id.readline()
        else:
            file_list_id.close()
            break
