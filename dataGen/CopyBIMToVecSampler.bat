TITLE Copying files...
set buildSource=D:\Works\myPrograms\BIMToVec\BIMToVecSampler\BIMToVecSampler\bin\Release
set target=D:\Works\myPrograms\BIMToVec\dataGen\BIMToVecSampler

RMDIR /S /Q %target%
MKDIR %target%
XCOPY %buildSource% %target% /S /E /Y
ECHO All the files are copied
TIMEOUT 3