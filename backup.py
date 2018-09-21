import subprocess
import Subtitle
import Sound
import glob
import time
import sys
import os

def extractSubtitleData(filename):
    """
    loop over Subtitle file to get each sub data
    example :
        5                                                            (Subtitle index)
        00:00:21,560 --> 00:00:25,000                                (Subtitle duration)
        improve the ability of the jackboot to talk like a human.    (Subtitle text)
    Args :
        filename(string) - subtitle filename (usually .srt file)
    Return :
        idx(list)(int) - contains indecies of all subtitles
        duration(list)(string) - contains Time of each subtitle in the form (00:00:21,560 --> 00:00:25,000)
        text(list)(string) - contains text of each subtitle
    """
    index = []
    timePeriod = []
    text = []

    with open(filename,"r") as f:
        for line in f.readlines():
            if line == "\n":            
                continue
            try:
                if int(line):                                
                    # sys.stdout.write(line)
                    index.append(int(line[:len(line)-1]))
            except :
                if line.startswith("0"):                                        
                    timePeriod.append(line[:len(line)-1])
                else:                
                    text.append(line[:len(line)-1])                    
    return index,timePeriod,text

def manupilateSubtitleData(index,Time,text):
    """
    manupilate subtitle raw data to get start_time ,end_time , duration for each subtitle 
    example :
        raw time ( 00:00:21,560 --> 00:00:25,000 )
        start (21.56) , end (25.00) , duration (3.44)
    Args :
        index(list)(int) - contains indecies of all subtitles
        Time(list)(string) - contains Time of each subtitle in the form (00:00:21,560 --> 00:00:25,000)
        text(list)(string) - contains text of each subtitle
    Return :
        (list)(tuple) - contains 4 objects ( start_time , end_time , duartion , text )
    """
    duration = [] # contain duration_period for each subtitle
    fullTime = [] # contain tuples of (start_time , end_time) for each subtitle
    # timeCopy = []
    # print(len(index),index[0])
    for idx in index:
        # print(idx,Time[idx-1])
        start_to_end_time = Time[idx-1].split(" --> ") # list of start and end times for a subtitle

        # start_to_end_time[0] = start_to_end_time[0][:12]
        # start_to_end_time[1] = start_to_end_time[1][:12]

        start_time = [int(i) if len(i.split(",")) == 1 else i for i in start_to_end_time[0].split(":")] # start time digits [hours, minutes, seconds]
        end_time = [int(i) if len(i.split(",")) == 1 else i for i in start_to_end_time[1].split(":")] # end time digits [hours, minutes, seconds]
        # for the check above >> because of seconds in subtitle time (it's in the form of 29,560 ) 

        # convert each digit into seconds to get start , end & duration
        start_seconds = [int(i) for i in start_time[2].split(",")]
        start = start_time[0] * 60 * 60 + start_time[1] * 60 + start_seconds[0] + start_seconds[1]/1000

        end_seconds = [int(i) for i in end_time[2].split(",")]
        end = end_time[0] * 60 * 60 + end_time[1]*60 + end_seconds[0] + end_seconds[1]/1000

        duration_period = end - start 

        # print(start_to_end_time[0],start)
        # print(start_to_end_time[1],end)
        # print(round(duration_period,4),"\n")

        fullTime.append((start,end))
        # timeCopy.append((start,end))
        duration.append(duration_period)

    for idx in range(len(fullTime)):
        """
        problem 1:
            to solve the problem of sound small segments that aren't available between subtitles
            if newStart != oldEnd:
                newStart -= (newStart - oldEnd) / 2
                oldEnd += (newStart - oldEnd) / 2
        problem 2:
            if the start of newSub is the same as the last endSub (not fixed yet)
        """
        if idx == 0:
            duration[idx] = fullTime[idx][1] - fullTime[idx][0]
            continue

        if fullTime[idx][0] != fullTime[idx-1][1] : 
            diff = fullTime[idx][0] - fullTime[idx-1][1]
            fullTime[idx] = (fullTime[idx][0] - (diff/2) , fullTime[idx][1] )
            fullTime[idx-1] = (fullTime[idx-1][0], fullTime[idx-1][1] + (diff/2))

        duration[idx] = fullTime[idx][1] - fullTime[idx][0]
        
    # for i,j in zip(fullTime,timeCopy):
        # print("start(",str(i[0]) + " "-j[0],")\nend(",str(i[1]) + " "-j[1],")\n")
    return [(round(fullTime[i-1][0],3), round(fullTime[i-1][1],3), round(duration[i-1],3), text[i-1]) for i in index]
    
def saveSubtitleData(filename,SubtitleData):
    """
    write subtitle data as .txt file with name of the original .srt file
    Args :
        filename(string) - subtitle filename (usually .srt file)
        SubtitleData(list)(tuple) - contains 4 objects ( start_time , end_time , duartion , text )
    Return :
        None
    """
    f = open(filename.split(".")[0]+"Data.txt","w")

    for i in SubtitleData:
        f.writelines(str(i[0]) + " " + str(i[1]) + " " + str(i[2]) + " " + str(i[3]) + " " + "\n")

    f.close()
    
def soundSegment(start,duration,inputFile,outputFile,inDir,outDir):
    """
    grap the inputFile from input directory (inDir) 
    make an audio segment of it either audio or video 
    from start position with specifeied duration 
    save it as outputFile into output directory (outDir)
    Args:
        start(int) - start position in seconds
        duration(int) - time period of segment in seconds
        inputFile(string) - either audio or video
        outputFile(string) - audio file (usually .wav)
        inDir(string) - input Directory
        outDir(string) - output Directory
    Return:
        None
    """
    inputFile = inputFile.split("\\")[len(inputFile.split("\\"))-1] # get exact name from full Path
    outputFile = outputFile.split("\\")[len(outputFile.split("\\"))-1] # get exact name from full Path
    FILE = open(outDir + "\\" + outputFile,"w") # create segment file
    print("------ Segmentation is On {} ------".format(inputFile))
    cmdCommand = ["E:\\Programs\\ffmpeg\\bin\\ffmpeg.exe","-ss",str(start),"-t",str(duration),"-i",inDir + "\\\\" + inputFile,"-acodec","libmp3lame","-ab","128k",outDir +"\\\\"+ outputFile]

    # cmdCommand = ("E:\\Programs\\ffmpeg\\bin\\ffmpeg.exe" + " -ss " + str(start) + " -t " + str(duration) + " -i " + inDir + "\\" + inputFile + " -acodec libmp3lame -ab 128k " + outDir +"\\"+ outputFile).split(" ")

    output = subprocess.Popen(cmdCommand, stdin=subprocess.PIPE ,stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, universal_newlines=True)    
    output.communicate(input="y")    # in case of "file already exists . Overwrite ? [y/N]"
    # print(output.stdout)
    print("------ Segmentation Over & Out To {} ------\n".format(outDir +"\\"+ outputFile))
    FILE.close()

def workOnMovie(movieName,subtitleName):
    """
    make sound Segmentation for the whole movie by its subtitle frames
    Args:
    movieName(string) - name of the movie
    subtitleName(string) - name of subtitle file (usually .srt)
    Return:
        None
    """
    # print(subtitleName)
    # print("\\".join(fileDirectorylist[:len(fileDirectorylist)-1]))
    index,timePeriods,SubText = Subtitle.extractSubtitleData(subtitleName)
    subtitleChunks = Subtitle.manupilateSubtitleData(index,timePeriods,SubText)
    Subtitle.saveSubtitleData(subtitleName,subtitleChunks)

    fileDirectorylist = movieName.split(movieName[len(movieName)-4:])[0].split("\\") # get full path as a list 

    fileDirectory = "\\".join(fileDirectorylist[:len(fileDirectorylist)-1]) # get only the directory 
    segmentsDir = fileDirectory + "\Segments" # segments folder path within the movie directory 
    
    try:
        os.mkdir(segmentsDir) # create segments folder 
    except FileExistsError:
        pass

    segmentsDir = segmentsDir.replace("\\","\\\\") # path issues ( may be fixed later)
    fileDirectory = fileDirectory.replace("\\","\\\\") # same as above

    idx = 0 # keep count of the segments for naming the files 
    for segment in subtitleChunks:
        Sound.soundSegment(segment[0],segment[2],movieName,"segment"+str(idx)+".wav",fileDirectory,segmentsDir)
        idx += 1

def Run(inDir):
    """
    Main Function 
    Args:
        inDir(string) - root folder that have all the movies
    Return:
        None
    """
    root = inDir

    Movies = [] # contain every movie in Directory
    SRTs = [] # contain every subtitle in Directory

    for folder in glob.glob(root + "*"):  
        for movie in glob.glob(folder + "\*"):        
            if ".mkv" in movie or ".mp4" in movie or ".avi" in movie:    
                # print(movie)
                Movies.append(movie)
            if ".srt" in movie and ".style" not in movie: 
                SRTs.append(movie)

    for movie,srt in zip(Movies,SRTs):
        workOnMovie(movie,srt)
    

"""
if __name__ == "__main__":
    
    start = time.time()
    rootDir = "E:\\Movies\\ANIMATION\\"
    Run(rootDir)

    print("Done in ",time.time() - start)

#---TESTING Subtitle Manupilation ---#

inputFile = "EscapePlan2Hades.brrip.2018.1080p.srt"

index,Time,SubText = extractSubtitleData(inputFile)

subtitleChunks = manupilateSubtitleData(index,Time,SubText)

saveSubtitleData(inputFile,subtitleChunks)

#-----TESTING Sound -----#
start = 6.050
duration = 3.590
inputFile = "test2.mp4"
outputFile = "cmdTest03.wav"
directory = "E:\\graduationProject\\MoviesData\\test\\"

soundSegment(start,duration,inputFile,outputFile,directory,directory)
"""