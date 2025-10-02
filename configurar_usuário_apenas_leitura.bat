@echo off
setlocal

:: Set environment variables for the current user
setx caixas_box_db_user "caixas_box_readonly"
setx caixas_box_db_password "H*($XGgzJSm#cO,"

:: Display confirmation
echo.
echo Environment variables set successfully!
echo.

pause

endlocal