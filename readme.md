This Python script takes in a Monash Moodle gradebook HTML page, and calculates the weighted average mark.

Save your gradebook page with Ctrl+S, and open that file after running the script.
It requires the individual weights of each assignment to be listed in the name, and no overlapping weights.

If your weights do not yet reach 100%, it allows you to add custom results.

Requires BeautifulSoup4: `pip install bs4`
