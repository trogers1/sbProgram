import gl
from flask import Flask, render_template, redirect, \
    url_for, request, session, flash, jsonify
import requests
import json
import pysb
import sys
import time

from pprint import pprint

sb = pysb.SbSession()

totalDataCount = 0
projectDictNumber = 0
possibleProjectData = []
exceptionFound = False
lookedForShortcutsBefore = False
lookedForDataBefore = False
FYprojects = []

firstFYParse = True
veryFirstFYParse = True


def main(fiscalYear):
    resetGlobals()
    gl.Current_Item = fiscalYear
    global possibleProjectData
    possibleProjectData[:] = []
    print("parseFY.py main") # Quantico
    select_project(fiscalYear)

def exceptionLoop(item):
    import exceptionRaised
    exceptionRaised.main(item)
    if exceptionRaised.worked is True:
        return
    elif exceptionRaised.worked is False:
        exceptionLoop(item)

def select_project(fiscalYear):
    global possibleProjectData
    possibleProjectData[:] = []
    global firstFYParse
    global FYprojects
    global projectDictNumber
    global veryFirstFYParse
    if firstFYParse is True:
        projectDictNumber = 0
        getProjects(fiscalYear)
        firstFYParse = False
    # if projectDictNumber == -99999999999999:
    #     return
    print(FYprojects)  # Quantico
    print("Project dict number: "+str(projectDictNumber))  # Quantico
    try:
        currentProject = FYprojects[projectDictNumber]
    except IndexError:
        return
    print("currentProject: "+str(currentProject))  # Quantico
    getProjectData(possibleProjectData, FYprojects,
                   currentProject, exceptionFound,
                   )

def resetGlobals():
    global totalDataCount
    totalDataCount = 0
    global projectDictNumber
    projectDictNumber = 0
    global possibleProjectData
    possibleProjectData[:] = []
    global exceptionFound
    exceptionFound = False
    global lookedForShortcutsBefore
    lookedForShortcutsBefore = False
    global lookedForDataBefore
    lookedForDataBefore = False
    global FYprojects
    FYprojects[:] = []
    global firstFYParse
    firstFYParse = True
    global veryFirstFYParse
    veryFirstFYParse = True


def getProjects(fiscalYear):
    global possibleProjectData
    global projectDictNumber
    possibleProjectData[:] = []
    global FYprojects
    FYprojects[:] = []
    print(fiscalYear)
    currentFYprojects = sb.get_child_ids(fiscalYear)
    print(currentFYprojects)  # Quantico
    for project in currentFYprojects:
        projectJson = sb.get_item(project)
        try:
            if "Project" in projectJson["browseCategories"] and project not in FYprojects:
                print("--Item is a project.")
                FYprojects.append(project)
            elif "Project" in projectJson["browseCategories"] and project in FYprojects:
                print("--Item already parsed.")
            else:
                print("browseCategories = "+str(projectJson["browseCategories"]))
        except KeyError:
            print("--"+str(project)+" not a project.")
            print("Quickly parsing "+str(i)+" to determine what it is...")
            print("======================================================")
            gl.onTheFlyParsing.append(i)
            import parse
            parse.parseOnTheFly()
            print("Back to finding projects...")
            main(fiscalYear)
    return FYprojects



def getProjectData(possibleProjectData, FYprojects,
                   currentProject, exceptionFound,
                   ):
    global lookedForDataBefore
    projectItems = sb.get_child_ids(currentProject)
    try:
        currentProjectJson = sb.get_item(currentProject)
    except Exception:
        exceptionFound = True
        exceptionLoop(currentProject)
        currentProjectJson = sb.get_item(currentProject)

        # Old exception handling:
        # print("--------Hit upon a 404 exception: " +
        #       str(currentProject) + " (1)")
        # import exceptionRaised
        # exceptionRaised.main(currentProject)
        # if exceptionRaised.worked is True:
        #    currentProjectJson = sb.get_item(currentProject)
        # elif exceptionRaised.worked is False:
        #     getProjectData(possibleProjectData, FYprojects,
        #                    currentProject, exceptionFound,
        #                    )
        # else:
        #     print('Something went wrong. Function: getProjectData (1)')
    if lookedForDataBefore is False:
        populateGPYLists(currentProject, currentProjectJson)
        print("""

        Currently searching '"""+str(currentProjectJson['title'])+"'.")
        # flash("""

        # Currently searching '"""+str(currentProjectJson['title'])+"'.")
        lookedForDataBefore = True
        for i in projectItems:
            try:
                currentProjectItemJson = sb.get_item(i)
            except Exception:
                exceptionFound = True
                exceptionLoop(i)
                currentProjectItemJson = sb.get_item(i)
            print(currentProjectItemJson['title'])
            if currentProjectItemJson['title'] == "Approved DataSets":
                possibleProjectData_Set = set()
                possibleProjectData_Set.update(possibleProjectData)
                try:
                    ancestors = sb.get_ancestor_ids(i)
                except Exception:
                    exceptionFound = True
                    print("--------Hit upon a 404 exception: " + str(i) + " (22)")
                    exceptionLoop(i)
                    ancestors = sb.get_ancestor_ids(i)
                    # Old exception handling:
                    # import exceptionRaised
                    # exceptionRaised.main(i)
                    # if exceptionRaised.worked is True:
                    #     children = sb.get_child_ids(currentId)
                    # elif exceptionRaised.worked is False:
                    #     gl.Exceptions.append(i)
                    #     print("-----------ERROR: Could not get project data.")
                    #     continue
                    # else:
                    #     print('Something went wrong. Function: getProjectData() (2)')
                for item in ancestors:
                    if item not in possibleProjectData_Set:
                        possibleProjectData_Set.add(item)
                        possibleProjectData.append(item)
                    else:
                        pass
                print('First look at Possible Project Data:')
                print(possibleProjectData)
                print('Total Items:')
                print(len(possibleProjectData))
            else:
                pass
    parse(possibleProjectData, FYprojects, projectItems,
          currentProject, exceptionFound,
          currentProjectJson)


def populateGPYLists(currentProject, currentProjectJson):
    gl.ID.append(currentProject)
    print(gl.ID)  # Quantico
    gl.URL.append(sb.get_item(currentProject)['link']['url'])
    print(gl.URL)
    gl.ObjectType.append("Project")
    print(gl.ObjectType)  # Quantico
    gl.Name.append(currentProjectJson["title"])
    print(gl.Name)  # Quantico
    findCurrentProjectFY(currentProject, currentProjectJson)
    print(gl.FiscalYear)  # Quantico
    gl.Project.append("Self")
    print(gl.Project)  # Quantico
    return

def printAllGLists():
    print(gl.ID)  # Quantico
    print(gl.URL)
    print(gl.ObjectType)  # Quantico
    print(gl.Name)  # Quantico
    print(gl.FiscalYear)  # Quantico
    print(gl.Project)  # Quantico
    print(gl.DataInProject)  # Quantico
    print(len(gl.DataPerFile)) # Quantico
    print(gl.RunningDataTotal)  # Quantico

def findCurrentProjectFY(currentProject, currentProjectJson):
    currentId = currentProject[:]
    json = currentProjectJson
    parentId = currentProjectJson["parentId"]
    try:
        children = sb.get_child_ids(currentId)
    except Exception:
        exceptionFound = True
        print("--------Hit upon a 404 exception: "+str(currentId)+" (1)")
        exceptionLoop(currentId)
        children = sb.get_child_ids(currentId)

        # import exceptionRaised
        # exceptionRaised.main(i)
        # if exceptionRaised.worked is True:
        #     children = sb.get_child_ids(currentId)
        # elif exceptionRaised.worked is False:
        #     FY = "Exception Raised: Could not find Fiscal Year"
        #     print("Exception Raised: Could not find Fiscal Year.")
        #     gl.FiscalYear.append(FY)
        #     return
        # else:
        #     print('Something went wrong. Function: findCurrentProjectFY() (2.2)')
    try:
        child = children[0]
    except (KeyError, IndexError) as error:
        print("No children of the current item.")
        currentId = parentId[:]  # this makes a slice that is the whole list.
        json = sb.get_item(currentId)
        parentId = json['parentId']
        children = sb.get_child_ids(currentId)
        child = children[0]
    try:
        childJson = sb.get_item(child)
    except Exception:
        exceptionFound = True
        print("--------Hit upon a 404 exception: " + str(child) + " (1)")
        exceptionLoop(child)
        childJson = sb.get_item(child)
    if 'FY' in json['title']:
        print("Item is a Fiscal Year")  # Quantico
        gl.fiscalYears.append(json['title'])
        return
    control = True
    while control is True:
        try:
            while 'Project' not in childJson['browseCategories']:
                currentId = parentId[:]  # this makes a slice that is the whole list.
                json = sb.get_item(currentId)
                parentId = json['parentId']
                children = sb.get_child_ids(currentId)
                child = children[0]
                childJson = sb.get_item(child)
                print("Not a Fiscal Year.")  # Quantico
        except KeyError:
            currentId = parentId[:]  # this makes a slice that is the whole list.
            try:
                json = sb.get_item(currentId)
            except Exception:
                exceptionFound = True
                print("--------Hit upon a 404 exception: " + str(currentId) + " (2)")
                exceptionLoop(currentId)
                json = sb.get_item(currentId)


            
            parentId = json['parentId']
            try:
                children = sb.get_child_ids(currentId)
            except Exception:
                exceptionFound = True
                print("--------Hit upon a 404 exception: "+str(currentId)+" (1)")
                exceptionLoop(currentId)
                children = sb.get_child_ids(currentId)
                # import exceptionRaised
                # exceptionRaised.main(currentId)
                # if exceptionRaised.worked is True:
                #     children = sb.get_child_ids(currentId)
                # elif exceptionRaised.worked is False:
                #     continue
                # else:
                #     print('Something went wrong. Function: findCurrentProjectFY (1)')
            child = children[0]
            try:
                childJson = sb.get_item(child)
            except Exception:
                exceptionFound = True
                print("--------Hit upon a 404 exception: " + str(child) + " (1)")
                exceptionLoop(child)
                childJson = sb.get_item(child)
                # import exceptionRaised
                # exceptionRaised.main(child)
                # if exceptionRaised.worked is True:
                #     hildJson = sb.get_item(child)
                # elif exceptionRaised.worked is False:
                #     continue
                # else:
                #     print('Something went wrong. Function: parse (1)')

            print("Not a Fiscal Year.")
            continue
        if 'Project' in childJson['browseCategories']:
            control = False
    FY = json['title'].replace(" Projects", "")
    print("appending \'"+str(json['title'])+'\' as '+str(FY))  # Quantico
    gl.FiscalYear.append(FY)
    return

    #do a "while" loop here. Something like, while the children of the current thing are NOT projects...
    #and when they are, take the ['title'] and append that to gl.FiscalYear and return

def parse(possibleProjectData, FYprojects, projectItems,
          currentProject, exceptionFound,
          currentProjectJson):
    possibleProjectData_Set = set()
    for i in possibleProjectData:
        possibleProjectData_Set.update(possibleProjectData)
        try:
            ancestors = sb.get_ancestor_ids(i)
        except Exception:
            exceptionFound = True
            print("--------Hit upon a 404 exception: "+str(i)+" (1)")
            exceptionLoop(i)
            ancestors = sb.get_ancestor_ids(i)
            # import exceptionRaised
            # exceptionRaised.main(i)
            # if exceptionRaised.worked is True:
            #     ancestors = sb.get_ancestor_ids(i)
            # elif exceptionRaised.worked is False:
            #     continue  # eyekeeper make sure this continues on to the next i in possibleProjectData.
            # else:
            #     print('Something went wrong. Function: parse (1)')
        for item in ancestors:
            if item not in possibleProjectData_Set:
                possibleProjectData_Set.add(item)
                possibleProjectData.append(item)
            elif item in possibleProjectData_Set:
                pass
            else:
                print("Something went wrong. Current function: "
                      + "getProjectData (1)")
    print('Double checked Possible Project Data:')
    print(possibleProjectData)
    print('Total Items:')
    print(len(possibleProjectData))

    findShortcuts(FYprojects, currentProject, exceptionFound,
                  possibleProjectData, projectItems, currentProjectJson,
                  )


def findShortcuts(FYprojects, currentProject, exceptionFound,
                  possibleProjectData, projectItems, currentProjectJson,
                  ):
    global lookedForShortcutsBefore
    global lookedForDataBefore
    print("Looking for shortcuts in any items...")
    foundShortcutsThisTime = False
    if lookedForShortcutsBefore is False:
        lookedForShortcutsBefore = True
        for i in projectItems:
            try:
                currentProjectItemJson = sb.get_item(i)
            except Exception:
                exceptionFound = True
                print("--------Hit upon a 404 exception: " + str(i) + " (1)")
                exceptionLoop(i)
                currentProjectItemJson = sb.get_item(i)
            if currentProjectItemJson['title'] == "Approved DataSets":
                try:
                    shortcuts = sb.get_shortcut_ids(i)
                except Exception:
                    exceptionFound = True
                    print("--------Hit upon a 404 exception: " + str(i) + " (1)")
                    exceptionLoop(i)
                    shortcuts = sb.get_shortcut_ids(i)
                print("Shortcuts in Approved DataSets:")  # Quantico
                print(shortcuts)
                if shortcuts == []:
                    lookedForShortcutsBefore = True
                    print("No shortcuts in \"Approved DataSets\".")
                elif shortcuts != []:
                    lookedForShortcutsBefore = True
                    foundShortcutsThisTime = True
                    for i in shortcuts:
                        if i not in possibleProjectData:
                            possibleProjectData.append(i)
                    print("We found some shortcuts and added them to the " +
                            "Possible Project Data:")
                    print(shortcuts)
                    print('Total Items added:')
                    print(len(shortcuts))
                    print("New Possible Project Data:")
                    print(possibleProjectData)
                    print("Current Item total:")
                    print(len(possibleProjectData))
                else:
                    print("Something went wrong. Current function: "
                            + "findShortcuts (1)")
                    exit()
            else:
                pass
                # elif exceptionRaised.worked is False:
                #     continue
                # else:
                #     print('Something went wrong. Function: findShortcuts (1.1)')

    elif lookedForShortcutsBefore is True:
        pass #something should happen here. eyekeeper
    else:
        print("Something went wrong. Current function: findShortcuts (2)")
        exit()
    allShortcuts = []
    allShortcuts[:] = []
    for i in possibleProjectData:
        try:
            preShortcuts = sb.get_shortcut_ids(i)
        except Exception:
            exceptionFound = True
            print("--------Hit upon a 404 exception: " + str(i) + " (1)")
            exceptionLoop(i)
            preShortcuts = sb.get_shortcut_ids(i)
            # import exceptionRaised
            # exceptionRaised.main(i)
            # if exceptionRaised.worked is True:
            #     preShortcuts = sb.get_shortcut_ids(i)
            #     for item in preShortcuts:
            #         if item not in allShortcuts:
            #             allShortcuts.append(item)
            # elif exceptionRaised.worked is False:
            #     continue
            # else:
            #     print('Something went wrong. Function: findShortcuts (2.2)')
            # print("preShortcuts: ")  # Quantico
            # print(preShortcuts)  # Quantico
        for item in preShortcuts:
            if item not in allShortcuts:
                allShortcuts.append(item)
        
    print("All shortcuts:")  # Quantico
    print(allShortcuts)  # Quantico
    if allShortcuts == []:
        print("No shortcuts in \"Possible Project Data\".")
    elif allShortcuts != []:
        #foundShortcutsThisTime = True
        for i in allShortcuts:
            if i not in possibleProjectData:
                foundShortcutsThisTime = True
                possibleProjectData.append(i)
        print("We found some shortcuts and added them to the Possible Project "
              + "Data:")
        print(possibleProjectData)
        print('Total Items:')
        print(len(possibleProjectData))
    else:
        print("Something went wrong. Current function: findShortcuts (3)")
        exit()

    if foundShortcutsThisTime is True:
        print("-------- Found shortcuts this time!")
        getProjectData(possibleProjectData, FYprojects, currentProject, exceptionFound,
                           )
    elif foundShortcutsThisTime is False:
        print("-------- Didn't find any Shortcuts this time!") # Quantico

        import countData_proj
        countData_proj.main(currentProject, possibleProjectData)
        #Now we collect all Project file info in ProjectFileDict:
        gl.ProjFileDict[currentProject] = {}
        currProj = gl.ProjFileDict[currentProject]
        currProj['Num_Of_Files'] = gl.NumOfFiles
        currProj['Project_Files'] = gl.ProjFiles

        #then we reset all global project file values:
        gl.NumOfFiles = 0
        gl.ProjFiles[:] = []
        print("""=================================================================
                Here is projItems as it currently stands: """)
        print(gl.ProjItems)

        if exceptionFound is False:
            print('''
            I am done looking through the \''''+str(currentProjectJson['title']) +
                  '''' project folder.''')
            global projectDictNumber
            # flash("Total Data in Project: ")
            # flash(gl.DataInProject[projectDictNumber])
            # flash("Running Total of Data thus far: ")
            # flash(gl.RunningDataTotal[projectDictNumber])
            projectDictNumber += 1
            whatNext(FYprojects, exceptionFound)

        elif exceptionFound is True:
            diagnostics(FYprojects, exceptionFound, currentProjectJson)
    else:
        print('Something went wrong. Current function: findShortcuts (4)')







def diagnostics(FYprojects, exceptionFound, currentProjectJson):
    print("There appear to have been exceptions raised during the parsing "+
          "process. Here is the list of IDs for items that raised exceptions "+
          "that were not solved:")
    print(gl.Exceptions)
    print('''

    I am done looking through the \''''+str(currentProjectJson['title']) +
          '''' project folder.''')
    global projectDictNumber
    # flash("Total Data in Project: ")
    # flash(gl.DataInProject[projectDictNumber])
    # flash("Running Total of Data thus far: ")
    # flash(gl.RunningDataTotal[projectDictNumber])
    # eyekeeper come back to this and add an option to try the exception raising items again.

    projectDictNumber += 1
    whatNext(FYprojects, exceptionFound)


def whatNext(FYprojects, exceptionFound):
    printAllGLists()
    global firstFYParse
    global projectDictNumber
    global lookedForShortcutsBefore
    global lookedForDataBefore
    if projectDictNumber >= len(FYprojects):
        print("You have finished one Fiscal Year. No more available Projects.")
        # flash("You have finished one Fiscal Year. No more available Projects.")
        # flash("""
        # ---------------------------------------------------------------------------------------
        # """)
        import countData_proj
        countData_proj.doneCountingFY()
        # excel()
        firstFYParse = True
        lookedForShortcutsBefore = False
        lookedForDataBefore = False
        gl.totalFYData = 0
        return
    elif projectDictNumber < len(FYprojects):
        print("Ok, let\'s start on project "+str(projectDictNumber+1) +
              " of "+str(len(FYprojects))+".")
        # flash("Ok, let\'s start on project "+str(projectDictNumber+1) +
        #       " of "+str(len(FYprojects))+".")
        # flash("""
        # ---------------------------------------------------------------------------------------
        # """)
        lookedForShortcutsBefore = False
        lookedForDataBefore = False
        select_project(gl.Current_Item)


def excel():        #  Quantico I took this out. 
    #print("""
    #Would you like to create an Excel Spreadsheet with all parsed data """+
    #"""currently in memory before continuing on? If you choose no, all """+
    #"""information gathered will continue to be compiled and will be """+
    #"""available to be included in a final spreadsheet at the end of """+
    #"""the process or to be used to create a speadsheet after each """+
    #"""subsequent Fiscal Year, Project, or Item that was originally """+
    #"""selected to be parsed is parsed.

    #(Y / N)""")
    #answer = input("> ").lower()
    if gl.Excel_choice == "Excel_for_each_FY":
        import ExcelPrint
        import editGPY
        ExcelPrint.main()
        editGPY.clearMemory()
    elif gl.Excel_choice == "One_Excel_for_all_FYs":
        pass
    else:
        print("Something wrong. No gl.Excel_choice selected.")
        sys.exit()



if __name__ == '__main__':
    # gl.itemsToBeParsed.append("5006c2c9e4b0abf7ce733f42")
    # gl.itemsToBeParsed.append("5006e94ee4b0abf7ce733f56")
    # gl.itemsToBeParsed.append("55130c4fe4b02e76d75c0755")
    # gl.itemsToBeParsed.append("55e07a67e4b0f42e3d040f3c")
    # gl.itemsToBeParsed.append("58111fafe4b0f497e79892f7")
    # gl.itemsToBeParsed.append("57daef3fe4b090824ffc3226")
    # main(fiscalYear)
    print("Set __name__ = '__main__' to something...")
