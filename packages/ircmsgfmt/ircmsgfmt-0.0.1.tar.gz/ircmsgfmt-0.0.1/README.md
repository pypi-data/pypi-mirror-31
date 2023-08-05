# IRC Formatter for Python

(Just a toy) XD

### Example:
```
from ircmsgfmt import formatter

msg = ":foo!~bar@127.0.0.1 PRIVMSG #test :Just for testing!"

fmt = formatter.formatter(msg)

print(fmt.channel(), fmt.nick())
```

### Output:
```
#test foo
```

#### Author: OriginCode
#### License: GPLv3
