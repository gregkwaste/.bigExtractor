#-------------------------------------------------------------------------------
# Name:        big extractor
# Purpose:     extract files from .big archive
#
# Author:      gregkwaste
#
# Created:     21/09/2014
# Copyright:   (c) gregkwaste 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

f=open('C:\\Users\\gregkwaste\\Downloads\\4557441-FFFFFFF15SG\\FIFA 15\\data_graphic2_extra.big','rb')


for i in range(15078,15080):
    f.seek(file_list[i][0]) #go to archive offset
    t=open('C://'+f.name(sep='\\')[-1].split('.')[0]+'//'+file_list[i][2],'wb')
    t.write(f.read(file_list[i][1]))
    t.close()


f.close()