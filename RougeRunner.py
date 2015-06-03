import os
import sys
import subprocess
import re
import unicodedata

### runRouge(goldSummary, testSummary)
### PARAMS  - goldSummary and testSummary are lists of sentences 
### RETURNS - Runs ROUGE on those summaries and returns an int from 0-1,
###           where a higher value represents a better match to GOLD

def compareUsingRouge(goldSummary, testSummary):
    goldFile = open("ROUGE/text_summarizer/models/1.html", 'w')
    testFile = open("ROUGE/text_summarizer/systems/1.html", 'w')
    writeSentencesToFile(goldSummary, goldFile)
    writeSentencesToFile(testSummary, testFile)
    goldFile.close()
    testFile.close()
    return runRouge()

### Helper funcrions follow
def runRouge():
    rougeOutput = subprocess.check_output(['perl', 'ROUGE-1.5.5.pl', '-e', 'ROUGE/data', '-f', 'A', '-a', '-x', '-s', '-m', '-2', '-4', '-u', 'ROUGE/text_summarizer/settings.xml'])
    
    # Return results 
    firstScoreMatch = re.search(r'Average_R: (.{7})', rougeOutput)
    firstScore = float(firstScoreMatch.group(1))
    
    secondScoreMatch = re.search(r'Average_P: (.{7})', rougeOutput)
    secondScore = float(secondScoreMatch.group(1))
    
    thirdScoreMatch = re.search(r'Average_F: (.{7})', rougeOutput)
    thirdScore = float(thirdScoreMatch.group(1))
    
    scores = [firstScore, secondScore, thirdScore]
    
    avgScore = sum(scores)/3
    return avgScore        
    
def writeSentencesToFile(sentences, fileToWrite):
    fileToWrite.write('<html>' + "\n");
    fileToWrite.write('<head><title>filename_here</title> </head>' + "\n")
    fileToWrite.write('<body bgcolor="white"> ' + "\n")

    for index in range (0, len(sentences)):
        fileToWrite.write('<a name=\"' + str(index+1) + '">[' + str(index+1) + ']</a> <a href="#' + str(index+1) + '" id=' + str(index+1) + '>')
        fileToWrite.write(sentences[index])
        fileToWrite.write('</a>'+"\n")

    fileToWrite.write('</body>'+"\n"+'</html>')    

### End of helper functions

### Sample output (uncomment to test)

#gold = ["What a day!", "It was awesome!", "This is a great summary.", "I hope this is accurate.", "Let's see how good this is.", "Hey, are you good?"]
#genSum = ["It was awesome!", "This is a grea|t summary.", "I hope this is accurate.", "Let's see how good this is.", "Hey, are you good?"]
#compareUsingRouge(gold, genSum)