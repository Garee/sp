result=$(python sp/sp.py -np travis-ci | wc -m);

if [ result = "0" ]; then
    echo "No search results found";
    exit 1;
else
    exit 0;
fi
