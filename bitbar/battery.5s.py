#!/usr/bin/env python3

import sys

sys.path.append('/opt/git/fenhl.net/syncbin-private/master/python')

import batcharge_macbook

BATTERY_IMAGE = 'iVBORw0KGgoAAAANSUhEUgAAACQAAAAkCAYAAADhAJiYAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAACXBIWXMAABYlAAAWJQFJUiTwAAABWWlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNS40LjAiPgogICA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPgogICAgICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgICAgICAgICB4bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyI+CiAgICAgICAgIDx0aWZmOk9yaWVudGF0aW9uPjE8L3RpZmY6T3JpZW50YXRpb24+CiAgICAgIDwvcmRmOkRlc2NyaXB0aW9uPgogICA8L3JkZjpSREY+CjwveDp4bXBtZXRhPgpMwidZAAAAmklEQVRYCe2S4QqAMAiEV/T+r1xsIRxM3RZJBtefxen0/GYp/EiABEiABHIT2Ax7p6FHys3LHtnhSW0aGlFbJVTf2dq7Ua+p+AFZXywytL9/Vwl1Bd4WkJBVW3si1DyymKfV7+6mI4QTdG6VkSR/Jle57kqtdjpCuEMyfR0jgoCLR4JoSDTvDDea7sloyNsHxkiABEiABP5A4AINSwgoISSBEQAAAABJRU5ErkJggg=='
BATTERY_IMAGE_CHARGING = 'iVBORw0KGgoAAAANSUhEUgAAACQAAAAkCAYAAADhAJiYAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAACXBIWXMAABYlAAAWJQFJUiTwAAABWWlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNS40LjAiPgogICA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPgogICAgICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgICAgICAgICB4bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyI+CiAgICAgICAgIDx0aWZmOk9yaWVudGF0aW9uPjE8L3RpZmY6T3JpZW50YXRpb24+CiAgICAgIDwvcmRmOkRlc2NyaXB0aW9uPgogICA8L3JkZjpSREY+CjwveDp4bXBtZXRhPgpMwidZAAAArklEQVRYCe2S2w6AIAxD0fj/v6zOB9JwGQMEMSlPBLquHOYcFwmQAAmQwNoEtky8M3M+8jiX5ek5O5Dvt498cov37wMJWo+3hUCp5gDB0EbQR91iIBGqk646vXQZBkrZpsjhmfYI1KW8o9rlhhpTl14jWtFYdOhr2XvP8Mv8xe0S4bQ492owEAbAYL09quoxkKUQQ1v01Zrlhnq5QNqXfTZH1f/MAhIgARIggYkELqLnECFMtglNAAAAAElFTkSuQmCC'

if batcharge_macbook.charging:
    if batcharge_macbook.charge < 0.3:
        print('{}%|templateImage={}'.format(int(batcharge_macbook.charge * 100), BATTERY_IMAGE_CHARGING))
        print('---')
        print('charging')
elif batcharge_macbook.charge < 0.7:
    print('{}%|templateImage={}'.format(int(batcharge_macbook.charge * 100), BATTERY_IMAGE))
    print('---')
    print('not charging')
