# Web Controller URLs
INDEX = "/"
SITE_ROOT = "/{path:str}"
SCHEDULES = "/schedules"

# League Controller URLs
SCHEDULE_INDEX = "/schedule"
STANDINGS_INDEX = "/standings"
LEAGUE_INDEX = "/league"
LEAGUE_SCHEDULE = "/schedule/{slug:str}"
LEAGUE_STANDINGS = "/standings/{slug:str}"
LEAGUE_STATS = "/league/stats"

# Team Controller URLs
TEAM_INDEX = "/team"
TEAM_SCHEDULE = "/team/schedule"
TEAM_STATS = "/team/stats"

MATCH_INDEX = "/match"

PLAYER_INDEX = "/player"

# ADMIN SECTION

# Account Controller URLs
ACCOUNT_LOGIN = "/access/login"
ADMIN_INDEX = "/iesl-admin"

ADMIN_SEASON = "/iesl-admin/season"
ADMIN_SEASON_CREATE = "/iesl-admin/season/create"
ADMIN_SEASON_EDIT = "/iesl-admin/season/{slug:str}"
ADMIN_SEASON_ATTACH_LEAGUES = "/iesl-admin/season/attach-leagues"
ADMIN_SEASON_END_DATE = "/iesl-admin/season/end-date"
ADMIN_SEASON_DELETE = "/iesl-admin/season/delete/{slug:str}"
ADMIN_SEASON_SEARCH = "/iesl-admin/season/search"

ADMIN_LEAGUE = "/iesl-admin/league"
ADMIN_LEAGUE_CREATE = "/iesl-admin/league/create"
ADMIN_LEAGUE_EDIT = "/iesl-admin/league/{slug:str}"
ADMIN_LEAGUE_DELETE = "/iesl-admin/league/delete/{slug:str}"
ADMIN_LEAGUE_SEARCH = "/iesl-admin/league/search"
ADMIN_LEAGUE_AGE_OVER = "/iesl-admin/league/age-over"

ADMIN_TEAM = "/iesl-admin/team"
ADMIN_TEAM_CREATE = "/iesl-admin/team/create"
ADMIN_TEAM_EDIT = "/iesl-admin/team/{slug:str}"
ADMIN_TEAM_DELETE = "/iesl-admin/team/delete/{slug:str}"
ADMIN_TEAM_SEARCH = "/iesl-admin/team/search"

ADMIN_SCHEDULE = "/iesl-admin/schedule"
ADMIN_SCHEDULE_CREATE = "/iesl-admin/schedule/create"
ADMIN_SCHEDULE_LEAGUE = "/iesl-admin/schedule/league-link"
ADMIN_SCHEDULE_VIEW = "/iesl-admin/schedule/{slug:str}"
ADMIN_SCHEDULE_EDIT = "/iesl-admin/schedule/edit/{slug:str}"
ADMIN_SCHEDULE_PUSH = "/iesl-admin/schedule/push/{fixture.id:str}"
ADMIN_SCHEDULE_DELETE = "/iesl-admin/schedule/delete/{slug:str}"
ADMIN_SCHEDULE_SEARCH = "/iesl-admin/schedule/search"
ADMIN_SCHEDULE_GENERATE = "/iesl-admin/schedule/generate"

ADMIN_FIXTURE_CREATE = "/iesl-admin/fixture/create"
ADMIN_FIXTURE_EDIT = "/iesl-admin/fixture/{fixture_id:str}"
ADMIN_FIXTURE_DELETE = "/iesl-admin/fixture/delete/{fixture_id:str}"

ADMIN_PLAYER = "/iesl-admin/player"
ADMIN_PLAYER_CREATE = "/iesl-admin/player/create"
ADMIN_PLAYER_EDIT = "/iesl-admin/player/{player_id}"

ADMIN_USER = "/iesl-admin/user"
ADMIN_USER_CREATE = "/iesl-admin/user/create"
ADMIN_USER_EDIT = "/iesl-admin/user/{user_id}"
