# ladok_average
Calculate your grade average from Ladok.

## Installation
Use git clone to install ladok-average.
```bash
git clone git@github.com:adammansson/ladok_average.git
```

## Instructions
- Visit https://www.student.ladok.se/student/app/studentwebb/
- Log in
- Press "Transcripts and certificates" in the sidebar
- Press "Create"
- Select "National official transcript of records" as the type of transcript
- Uncheck all boxes under "Include"
- Select language of your choice
- Press "Create" again
- Download the transcript by pressing the first entry under "Created transcripts and certificates", it is called "Intyg.pdf" by default
- Place "Intyg.pdf" in the same directory as "script.py" or use the "--filename" flag when running the script
- Use ```python -m ladok_average -h``` for further help

## Usage examples
```bash
python -m ladok_average
```
```bash
python -m ladok_average another_filename.pdf -v
```
```bash
python -m ladok_average --includeug --ignoreaverage
```
```bash
python -m ladok_average -o=Uttyg.txt
```