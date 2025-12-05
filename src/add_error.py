def add_error_list(error_list, errorfile):
    if not error_list:
        return

    with open(errorfile, 'a') as f:
        for id in error_list:
            f.write(str(id) + "\n")