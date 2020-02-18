# Time-Decay-Constant
Python script to calculate time-decay constant values for time-domain electromagnetic data


> Install the Geosoft libraries and make sure you are signed in to your Geosoft ID. 
> Run TEM_Tau.py. >> 
> Select your GDB file. It should contain an array channel. Use Array Channel Profile viewer in Oasis to make sure that the array channel   starts at window 0 (i.e. ‘Total windows’ should be equal to the number of time gates of your data). 
> Make sure that your lines are selected in the database, and your database has room to add one new channel. Your database must not be       open in Geosoft while running the code, otherwise the code cannot write the new channel into the database.
> After selecting your database, click on ‘Read GDB file’. Then, from the drop-down menu, select your array channel. 
> Type the number of channels you would like for Tau calculation. 
> Open your time gates file in millisecond (see the sample sample .csv file).
> Set the noise level, assign a channel name to store calculated Tau in your database and click on ‘Tau calculation’. 
> You should see a bar showing the progress, and the processed lines printed in the console. 
> After the last line is processed, open your database in Oasis and check the calculated data. 


