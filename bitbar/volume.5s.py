#!/usr/local/bin/python3

import subprocess

MUTED = 'iVBORw0KGgoAAAANSUhEUgAAACQAAAAkCAYAAADhAJiYAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAACXBIWXMAABYlAAAWJQFJUiTwAAABWWlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNS40LjAiPgogICA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPgogICAgICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgICAgICAgICB4bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyI+CiAgICAgICAgIDx0aWZmOk9yaWVudGF0aW9uPjE8L3RpZmY6T3JpZW50YXRpb24+CiAgICAgIDwvcmRmOkRlc2NyaXB0aW9uPgogICA8L3JkZjpSREY+CjwveDp4bXBtZXRhPgpMwidZAAAA+0lEQVRYCc3V0Q7CMAgF0Gr88PnlWshooGMrTdbLlmxW0N4jfbCUdddWt/6t235uZ8E8AqQx6aAekwryMGmgM0wK6AoDB40wUFAEAwNFMRDQDGY5aBYzDfoUzP+NwF41z7ta/+11F9YkWEeYGhpEEA3Qa0bSCA9F7tz3kGMa5fDnkBMSmPdTWw8JIkgLVipTQ4O8YzM1JMgEqwnRsvVQoBa4Q+iYzFEJCgXaHfyiIXrNTTToAKgKU6M3/ThZeuPDBI72pQnRF6L3d7RhRn+roTTV6A0xzqAgIAqJomCgKAoKiqDgoBEqBXSFSgOdoVJBHiod1KMeAdKoKdAf1w2rln5sYTMAAAAASUVORK5CYII='
LOW = 'iVBORw0KGgoAAAANSUhEUgAAACQAAAAkCAYAAADhAJiYAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAACXBIWXMAABYlAAAWJQFJUiTwAAABWWlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNS40LjAiPgogICA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPgogICAgICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgICAgICAgICB4bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyI+CiAgICAgICAgIDx0aWZmOk9yaWVudGF0aW9uPjE8L3RpZmY6T3JpZW50YXRpb24+CiAgICAgIDwvcmRmOkRlc2NyaXB0aW9uPgogICA8L3JkZjpSREY+CjwveDp4bXBtZXRhPgpMwidZAAAA2UlEQVRYCe3V0QqAIAwFUIs+3D8vfbgwxrSN8q6HhCh1bKdFVcq6UVvqc136WGZgPgGSmHSQxqSCLEwaaIRJAc0wdNAdhgryYGggL4YCimCWg6KYMOgonP8NYFurNx37dPe9TUAAG2ZmgYYAvcEEubrEBOlmmPMfZLZFLP4dEs0wL5kdwjcIb1s6yAToRVaHXN3ROM+8tqCePHJ48j6KqV8D9buJoHo8ZdRWxfPoKBgU8aAQSzvfoWgQWWiGknHU6xGKitDFLJSOoc81ig6wCkqUtZ+yBlSo+AWz9q1+ipbe+wAAAABJRU5ErkJggg=='
HIGH = 'iVBORw0KGgoAAAANSUhEUgAAACQAAAAkCAYAAADhAJiYAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAACXBIWXMAABYlAAAWJQFJUiTwAAABWWlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNS40LjAiPgogICA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPgogICAgICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgICAgICAgICB4bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyI+CiAgICAgICAgIDx0aWZmOk9yaWVudGF0aW9uPjE8L3RpZmY6T3JpZW50YXRpb24+CiAgICAgIDwvcmRmOkRlc2NyaXB0aW9uPgogICA8L3JkZjpSREY+CjwveDp4bXBtZXRhPgpMwidZAAABEUlEQVRYCe2UjQ7DIAiEuz05b75h6zVOq6D402Q12RDwzm803baNW8TWn3H2dc6AuQVQCLMcKIZZCnQFswwoB7MEqAQzHUiCmQqkgZkGpIUpAbleqc9t3SI+BjNNDF1xHrU4R10diU/CRBtjc+hQ/8lf/gI0R8TwDrd3y0G4leTvoz78O7nY35iAzQJS/+KZQNKUduiZQKopPUDSmJ4J3WlCyX+Oh8Pbt6d/+8ik6cR96cmefeKdE9d8TrHfQIt6nKOujsQnYaKJoTHOoxbnqFdHYgXMpJgzhy7Xr64TK2BaitXGFoEGyuLfpJWgmkytohKU1btZn4NqNuwhvILq4WvyiKFMZr3EIVQvT7MPoKqMvgccyWgfMQBrAAAAAElFTkSuQmCC'

muted = subprocess.check_output(['osascript', '-e', 'output muted of (get volume settings)']).decode('utf-8') == 'true\n'
volume = int(subprocess.check_output(['osascript', '-e', 'output volume of (get volume settings)']).decode('utf-8'))

if muted:
    print('|templateImage={}'.format(MUTED))
elif volume < 6:
    print('|templateImage={}'.format(LOW))
elif volume > 13:
    print('|templateImage={}'.format(HIGH))
