import subprocess

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

"""
#-----TESTING-----#
start = 6.050
duration = 3.590
inputFile = "test2.mp4"
outputFile = "cmdTest03.wav"
directory = "E:\\graduationProject\\MoviesData\\test\\"

soundSegment(start,duration,inputFile,outputFile,directory,directory)
"""