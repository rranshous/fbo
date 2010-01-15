#!/usr/bin/python
# we are going to import the helper functions and re-generate the atom feed
URL = 'https://www.fbo.gov/index?mode=list&s=opportunity'
import sys
if __name__ == '__main__':
    import os
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    import pull
    rows = pull.get_rows(URL)
    items = pull.items_from_rows(rows)
    new_items = pull.append_archive(items)
    if new_items:
        pull.update_atom(new_items,file_path=sys.argv[1] if len(sys.argv) > 1 else None)
