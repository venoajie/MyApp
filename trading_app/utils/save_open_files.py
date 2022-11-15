import pickle

import os
#https://www.reddit.com/r/learnpython/comments/44essn/pickle_is_only_storing_files_into_home_directory/
BASEDIR = os.path.dirname(os.path.realpath(__file__))
print (BASEDIR)
def save_file_to_pickle (file_name: str, data: list, saved_directory:str=None)-> None:

    """
    https://stackoverflow.com/questions/11218477/how-can-i-use-pickle-to-save-a-dict-or-any-other-python-object
    """
        
    file_name=f"""{file_name}.pickle"""

    with open(file_name, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
def open_file_pickle (file_name: str, file_directory:str=None)-> None:

    """
    https://stackoverflow.com/questions/11218477/how-can-i-use-pickle-to-save-a-dict-or-any-other-python-object
    """
        
    #file_name=f"""{file_name}.{format}"""

    with open(file_name, 'rb') as handle:
        return pickle.load(handle)
        
def save_file_ (file_name, data, mode:str= 'w', format: str='csv')-> None:

    """
    mode: 'a'/'w' (append/write)
    format: 'csv'/'json'/'txt'
    """
    
    import csv
    
    print (data)
    field_name= list(data)
    
    file_name=f"""{file_name}.{format}"""
    pd.DataFrame(data).T.reset_index().to_csv('myfile.csv', header=False, index=False)
    print(field_name)
    print(file_name)
    
    with open(file_name, mode) as f:
        writer = csv.DictWriter(f, fieldnames=field_name)
        writer = csv.writer(f)
        writer.writerow(data)


#print (open_file_pickle('order_books.pickle'))
