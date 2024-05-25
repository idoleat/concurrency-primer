from datetime import datetime
import json
import sys

if __name__ == '__main__':
    if len(sys.argv) > 1: # we check if we received any argument
        if sys.argv[1] == "supports":
            # then we are good to return an exit status code of 0, since the other argument will just be the renderer's name
            sys.exit(0)

    # load both the context and the book representations from stdin
    context, book = json.load(sys.stdin)
    current_time = datetime.now().strftime("%B %d, %Y")

    # Could be more reliable to use <!--AddTimeHere--> in md as an easy-to-find anchor
    abstract = book['sections'][0]['Chapter']['content']
    insert_pos = abstract.find("## Abstract")

    if insert_pos != -1:
        abstract = abstract[:insert_pos-1] + f"{current_time}\n\n" + abstract[insert_pos-1:]
    else:
        updated_markdown = abstract

    book['sections'][0]['Chapter']['content'] = abstract

    # we are done with the book's modification, we can just print it to stdout,
    print(json.dumps(book))
