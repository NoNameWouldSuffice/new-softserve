from subprocess import call, STDOUT
from distutils.util import strtobool
import os
import sys

#YAARRGGHH

#This program is to somewhat automate the process to set up multiple remotes to
#A git repo and create a remote called all so they can all be updated
#Simutaneously

#There will be little no none checking for bad input when your using this and you
#Still have to go to each remote to make sure if the repo actually exists

if call(["git", "branch"], stderr=STDOUT, stdout=open(os.devnull, 'w')) != 0:
    print("ERROR: This has to be in a git repo dude")
    sys.exit()
else:
    remotes = [
    ("home", "ssh://git@atestofthis.duckdns.org:1341/home/git/git-repos/new-softserve"),
    ("github", "https://github.com/NoNameWouldSuffice/new-softserve.git")
    ]

    print("This will now create the following remotes in this git repo: \n")
    print("Name | Address")
    for i in range(0, len(remotes)):
        print("{0} | {1}".format(remotes[i][0], remotes[i][1]))
    print("\nThis will also create a remote called all which will contain\nall the above addresses and the master branch from this will be set \nas default upstream for this repo")
    print("\nIf you haven't already, ssh or connect to each repo to make \nsure that the git repos you've specified in the remotes actually exist already")
    confirm = strtobool(str(input("\nLast chance to back out. Continue ? (y|n)")))
    if not confirm:
        print("Aborting...")
        sys.exit()
    else:
        for i in range(0, len(remotes)):
            call(["git", "config", "--add", "remote.{0}.url".format(remotes[i][0]), str(remotes[i][1])])
            call(["git", "config", "--add", "remote.all.url", str(remotes[i][1])])

        print("done remote set")
        call(["git", "push", "-u", "all", "master"])
        print("Done pushing to all")
        call(["git", "config", "remote.all.fetch", "+refs/heads/*:refs/remotes/all/*"])
        print("Done setting fetch")
        print("Operation complete. Displaying list of remote in this repo.")
        call(["git", "remote", "-v"])
