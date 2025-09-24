@echo off
echo Setting up OpenAI API key for expert debates...
echo.
echo Instructions:
echo 1. Copy your OpenAI API key (starts with sk-...)
echo 2. Run this command in your terminal:
echo.
echo    set OPENAI_API_KEY=your_key_here
echo.
echo 3. Replace "your_key_here" with your actual key
echo.
echo Example:
echo    set OPENAI_API_KEY=sk-abc123def456...
echo.
echo 4. Then test the expert system:
echo    .venv\Scripts\python.exe tools\multi_backend_expert_debate.py
echo.
echo Note: The key will only be set for this terminal session.
echo For permanent setup, add it to your system environment variables.
echo.
pause