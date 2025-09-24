@echo off
REM Edit this file and replace YOUR_API_KEY_HERE with your actual OpenAI API key
REM Then run this batch file to set the environment variable and test

echo Setting OpenAI API Key...
set OPENAI_API_KEY=YOUR_API_KEY_HERE

echo Testing OpenAI connection...
.venv\Scripts\python.exe tools\test_openai_env.py

pause