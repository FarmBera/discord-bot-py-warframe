# Discord Bot for Warframe

- Python Toy Project for game called 'Warframe'

Request API to game server, receive data, and process response.
After processing response, notify (send latest content messages) to discord server.

## IMPORTANT NOTICE

### English

- Due to the sudden discontinuation of the API we were using, our current codebase is non-functional.
- We are planning to refactor the code with an alternative API as a top priority.
- There are some feature gaps with the new API. As a result, some of our existing functionality will be deprecated.

### 한국어 (Korean)

- 기존에 사용하던 API의 서비스가 갑작스럽게 종료되어 현재 코드가 정상 동작하지 않는 이슈가 있습니다.
- 최우선으로 대체 API를 적용하는 리팩토링을 진행할 예정입니다.
- 대체 API 사용에 따라, 기존에 지원되던 일부 기능이 제공되지 않을 수 있습니다.

## External Python Module Used

- discord.py: `v2.5.2`
- pyyaml: `v6.0.2`
- requests: `v2.32.4`

## Runtime Info

- Dev Env: Python `v3.13.3`, `v3.13.9`
- Runtime Env
    - option 1 : [Deployment Env] Ubuntu based Linux - Python `v3.12.3`
    - option 2 : Android Termux App - Python `v3.12.11`
