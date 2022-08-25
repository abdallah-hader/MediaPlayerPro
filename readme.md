#Media Player Pro
<Program designed for nvda screen reader users.
This program plays various media files and facilitates their control accessible 100% with screen readers.
In an easy way, where the user customizes what he wants from the speech within the program.
The program supports various media formats, including:
.mp3, .ogg, .wav, .m4a, .mp4.
etc.
# Features of the program:
1: speech  control, where you can select what you want from the available speech settings, which are as follows:
* Speak pause / resume.
* Speak the elapsed time when forward and rewind.
* Speak the volume when you control it.
2: You can open an entire folder in the program, and move around in files quite easily, and the features related to folders are as follows:
* The feature to delete a file is available from within the program.
* Folder search feature, you can run a file from the search results, and you can also copy the file path, or go to the file path and place the cursor on it through the context menu.
3: Load the entire folder after opening a file: This feature allows you to open the entire folder containing the played file.
4: Save the last played file with the position it was stopped at, after running the program it will reopen the file and move to the position it was stopped at, also if you open the folder in any way, it will reopen the folder when you run the program from its shortcut, and you can also Disable this feature in the settings.
5: Go to a file by typing the file number in the folder.
6: Play YouTube clips via the video link.
7: Search YouTube: Through this feature, you can search YouTube for videos and play them in the program. You can also copy the video link, or the link of the channel that contains the video, or open the video in the browser, or open the channel in the browser.
The YouTube search window contains a selection box, to load all the downloaded results into a list, and it becomes controlled as a folder, you can move between the results and the result will be played automatically.
Folders features also apply to the above feature, if the program is closed, it will keep these results and return them after opening the program.
By loaded results, I mean the results in the list, the more results you move to the end of the list, the more results will be loaded.
8: Read the comments of YouTube videos from within the program.
At first, only 20 comments will be uploaded, and when you reach the end of the list, more will be uploaded. This is to avoid some problems if there are a lot of comments.
9: Choose the forward seek 1/60 seconds, you can specify this from the settings, and you can forward the clip through numbers, not the side numbers, I mean the upper ones that are located at the top of the keyboard.
10: The feature of repeating the clip, that is, after it ends, the clip will be played again.
11: Go to the next clip feature: The clip repeat feature must be disabled for this feature to work, and this feature applies to folders and search results if available.
12: Control most of the program's features through global shortcuts with the ability to hide the program window.
You can open the files through the option that the program creates in the context menu after it is installed.
You can also set the program as the default program manually for the time being.
youtube tracks play as audio, not video.
# Program shortcuts:
I will put the program shortcuts from within, and the shortcut from the outside against it.
The control shortcut from the global program comes by default alt+control.
This shortcut is not compatible with Windows 11, so you can change this shortcut from the settings, and it is recommended to set it alt+windows+control for it to work fine.
I'll tell you every shortcut, then the global shortcut for it, but just the acronym, not to mention alt+control.
Left/Right Arrow:For forward / rewind, as well as the global shortcut itself.
Up / down arrow: to control the volume: 0/200%, as well as the general shortcut itself.
page up/ page down: to go to the next/previous track, as well as the global shortcut itself.
home: to go to the beginning of the clip, the global shortcut is the same.
space: to pause/resume, the global shortcut is the same.
m: to mute, global shortcut v.
n: To enable or disable the move to next file feature.
c: Shows comments if there is a YouTube video playing.
g: to move to a file by its number in the folder, i.e. its sequence between files, the global shortcut: j.
s: to search in the folder.
A: To search in YouTube, the global shortcut is the same.
y: to play a YouTube clip via the link, global shortcut: l.
r: To enable or disable the clip repeat feature, global shortcut: e.
i: For information on the track being played, the global shortcut is the same.
delete/numpad delete: to delete the track that is being played, this feature works only with folders at the moment, the global shortcut is the same.
control+o: to open a file, the global shortcut o.
control+f: to open a folder, global shortcut: s.
control+s: Opens settings.
control+w: Closes everything in the program, folder, or YouTube results, and stops the clip being played.
alt+windows+h: to hide/ show the program window.
The settings window is self-explanatory, because most of the options are described, and they are straightforward.
You can contact me through the about menu to give me your suggestions or inform me about a problem.
##changes
###changes1.3
* The program now open source
* Now when you run the program and it is already running it will tell you instead of nothing.
* Now when you search in YouTube and select the option to load results in a list, then let's say the fifth result is chosen to play, it will save the sequence of the result, and when you go to the next result, it starts from the sixth result, and so on with the automatic playback of the next clip.
* Another library was used to control sapi 5, and it may solve some problems that some face, such as controlling volume and speed.
Also, modifying the sapi5 settings did not require a restart of the program.
Also, now you can set the speed and volume from outside the settings, by pressing f5/f6 to control the speaking speed, f7/f8 to control the volume.
* Solve an issue where some shortcuts sometimes crash.
* Solve the problem of not being able to open settings after updating or deleting settings.
* Search history issues have been resolved.
* Solve the problem of muting the program after running it, which appeared to some people.
* Now you can run the program via the run window by typing mpp and the program will start directly.
* The acceleration and deceleration abbreviations for the clip have been changed from - and = to shift+down-arrow and shift+up-arrow-to-acceleration, since some brothers have reported that their keyboards do not have these marks due to their language.
* Additional keys for forward/rewind have been added as follows:
shift+right arrow: / left arrow: forward / backward by 10 seconds.
control+right arrow: / left arrow: forward/delay by 15 seconds.
control+shift+right arrow: / left arrow: forward / backward by 30 seconds.
alt+right arrow: / left arrow: forward/backward one minute.
As for the right arrow and the left, you can adjust the desired duration from the settings, and the possibility of customization has been increased from 60 seconds to 1800 seconds, which is approximately 30 minutes.
* The ability to search for the specific language update has been added, i.e. it is possible to issue an update for language files only so that they are easily updated, especially if an update is issued from the program and the translation of a language has not been completed if the translator is busy and so on, but so far this feature is not supported Arabic language, you can search for updates manually from the main menu, or activate the option to check the language update when starting, the verification is done on the basis of the program language, that is, if the program language is English, it does not come with updates for a language other than English.
* Now you can play from any direct link, that is, playback from a link is not limited to YouTube only.
Likewise, if you run anything through a link and you have its srt translation file on the computer and you open the srt file, it will be read without problems, that is, the translated thing is not required to be on your computer.
* Now when you open a subtitle file: only srt files will appear instead of all files
* The program now supports Turkish, French and Spanish languages.
