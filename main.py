import Subtitle
import glob
import time
import os
import Sound

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
    

if __name__ == "__main__":
    
    start = time.time()
    rootDir = "E:\\Movies\\ANIMATION\\"
    Run(rootDir)

    print("Done in ",time.time() - start)
