import pathlib
import os



'''
Normalize partner names 
    **should only be used for name duplication & other cleaning tasks, not final pipeline output:
- convert to lowercase
- clean special characters: .,()
- clean company tags?: inc, llc, co, ltd, etc.
- 
- standardize 'and': &, and, + --> &
'''
def normalize_name(name):
    # conver to lowercase
    anme = name.strip().lower()
    
    

'''
Eliminate duplicates
- substring matching
- flag potential abbreviation/expansion pairs (ex: roush fenway keselowski vs rfk)
'''