CREATE TABLE IF NOT EXISTS bets (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    internal_event_id   TEXT NOT NULL,
    sport               TEXT NOT NULL,
    league              TEXT NOT NULL,
    market_key          TEXT NOT NULL,
    selection_name      TEXT NOT NULL,
    odds_taken          REAL NOT NULL,
    pred_prob           REAL NOT NULL,
    ev_pct              REAL,
    full_kelly_pct      REAL,
    fractional_kelly_pct REAL,
    capped_stake_pct    REAL,
    stake               REAL NOT NULL,
    units               REAL,
    model_name          TEXT,
    model_version       TEXT,
    ticket_source       TEXT DEFAULT 'auto',
    event_start_time    TEXT,
    bet_placed_at       TEXT DEFAULT (datetime('now')),
    result              TEXT DEFAULT 'pending',  -- pending | win | loss | void
    pnl                 REAL,
    closing_odds        REAL,
    clv_pct             REAL
);

CREATE INDEX IF NOT EXISTS idx_bets_sport    ON bets(sport);
CREATE INDEX IF NOT EXISTS idx_bets_league   ON bets(league);
CREATE INDEX IF NOT EXISTS idx_bets_result   ON bets(result);
CREATE INDEX IF NOT EXISTS idx_bets_model    ON bets(model_name);
CREATE INDEX IF NOT EXISTS idx_bets_placed   ON bets(bet_placed_at);
