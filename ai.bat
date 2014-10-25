@echo off

echo AI

echo ==========================

set /P python=<apython.txt
%python% -m toontown.ai.ServiceStart --base-channel 342000000 --max-channels 9999999 --stateserver 10000 --district-name "Funny Farm" --astron-ip "127.0.0.1:7199" --eventlogger-ip "127.0.0.1:7197"

echo ==========================

pause