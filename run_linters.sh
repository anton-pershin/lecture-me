black lecture_me/

isort lecture_me/

printf "\nPress any key to continue to pylint...\n"
read -n 1 -s -r
pylint lecture_me/

printf "\nPress any key to continue to mypy...\n"
read -n 1 -s -r
mypy lecture_me/
