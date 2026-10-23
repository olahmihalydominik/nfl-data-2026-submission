"""Explicit bronze schemas (Spark DDL strings) for every raw CSV.

Never use `inferSchema` on bronze: types must be stable across runs. Column order = CSV header order
(checked by tests/test_schemas.py against the real files).

Read options every CSV needs:  header=true, nullValue="NA", timestampFormat for `time` columns.
Note: player_play.pass_result uses the empty string "" for "no dropback" -> keep it as "" (not null);
Spark's CSV reader does this by default for quoted empty strings, verify it in your bronze DQ check.
"""

COMBINE_RESULTS = """
    draft_year INT, nfl_id BIGINT, combine_position STRING, combine_height DOUBLE, combine_weight INT,
    hand_size DOUBLE, arm_length DOUBLE, wing_span DOUBLE, ten_yd_split DOUBLE, forty DOUBLE,
    vertical DOUBLE, broad_jump INT, three_cone DOUBLE, short_shuttle DOUBLE, bench_reps INT,
    ngs_athleticism_score INT, ngs_college_production_score INT, ngs_final_score INT
"""

COMBINE_TRACKING = """
    draft_year INT, event_id STRING, nfl_id BIGINT, entity_type STRING, time TIMESTAMP,
    drill_type STRING, drill_name STRING, attempt INT,
    x DOUBLE, y DOUBLE, s DOUBLE, a DOUBLE, dis DOUBLE, dir DOUBLE
"""

PLAYERS = """
    nfl_id BIGINT, display_name STRING, draft_year INT, nfl_position STRING, birth_date DATE,
    college_name STRING, college_conference STRING, draft_round INT, draft_pick_within_round INT,
    draft_overall_pick INT
"""

PLAYER_CAREER_SUCCESSES = """
    nfl_id BIGINT, career_offensive_snaps INT, career_defensive_snaps INT, career_special_teams_snaps INT,
    career_games_active INT, career_games_started INT, ap_all_pro_1st_team INT, ap_all_pro_2nd_team INT,
    pro_bowl_original_ballot INT
"""

GAMES = """
    game_id BIGINT, game_key BIGINT, season INT, season_type STRING, week INT,
    home_team_abbr STRING, visitor_team_abbr STRING
"""

GAME_TRACKING = """
    game_id BIGINT, play_id BIGINT, nfl_id BIGINT, time TIMESTAMP,
    x DOUBLE, y DOUBLE, s DOUBLE, a DOUBLE, dis DOUBLE, o DOUBLE, dir DOUBLE, event STRING
"""

PLAYER_PLAY = """
    game_id BIGINT, play_id BIGINT, team_abbr STRING, nfl_id BIGINT, lined_up_position STRING,
    play_description STRING, quarter INT, down INT, yards_to_go INT, possession_team STRING,
    yardline_side STRING, yardline_number INT, game_clock STRING, pre_snap_home_score INT,
    pre_snap_visitor_score INT, play_direction STRING, pre_snap_home_team_win_probability DOUBLE,
    pre_snap_visitor_team_win_probability DOUBLE, home_team_win_probability_added DOUBLE,
    visitor_team_win_probility_added DOUBLE, expected_points_added DOUBLE, expected_points DOUBLE,
    offense_formation STRING, receiver_alignment STRING, pass_result STRING, pass_length INT,
    play_nullified_by_penalty STRING, penalty_yards INT, pre_penalty_yards_gained INT, yards_gained INT,
    team_coverage_man_zone STRING, team_coverage_type STRING, in_motion_at_ball_snap BOOLEAN,
    target BOOLEAN, rec_yards INT, rush_yards INT, yards_after_catch INT, fumble INT, fumble_lost INT,
    route_ran STRING, separation_at_pass_forward DOUBLE, cushion DOUBLE, expected_yards_after_catch DOUBLE,
    dropback_duration DOUBLE, extended_sack_allowed DOUBLE, pass_rushers_encountered INT,
    peak_pressure_probability_allowed DOUBLE, pressure_allowed BOOLEAN, sack_allowed DOUBLE,
    time_to_pressure_allowed DOUBLE, quick_pressure BOOLEAN, unblocked_pressure BOOLEAN, blitzing BOOLEAN,
    player_get_off DOUBLE, sack DOUBLE, tackle INT, assist INT, caused_forced_fumble INT,
    recovered_fumble BOOLEAN, tackle_for_loss BOOLEAN, time_to_pressure DOUBLE, time_to_qb_hurry DOUBLE,
    coverage_assignment STRING, coverage_assignment_at_snap STRING
"""

# bronze table name -> DDL. Keys match conf/pipeline.yaml `raw_files`.
BRONZE_SCHEMAS: dict[str, str] = {
    "combine_results": COMBINE_RESULTS,
    "combine_tracking": COMBINE_TRACKING,
    "players": PLAYERS,
    "player_career_successes": PLAYER_CAREER_SUCCESSES,
    "games": GAMES,
    "game_tracking": GAME_TRACKING,
    "player_play": PLAYER_PLAY,
}


def ddl_columns(ddl: str) -> list[tuple[str, str]]:
    """Parse a DDL string into [(column, type), ...] without needing pyspark."""
    cols = []
    for part in ddl.replace("\n", " ").split(","):
        part = part.strip()
        if part:
            name, typ = part.split(None, 1)
            cols.append((name, typ.strip()))
    return cols
