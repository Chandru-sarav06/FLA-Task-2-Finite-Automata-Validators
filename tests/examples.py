"""Accepted / rejected examples used by the tests and the demo (>=5 each)."""
PIN_OK  = ["4829", "0731", "958216", "300450", "7392"]
PIN_BAD = ["482", "48290", "4829163", "48a9", "12 34", "", "-4829", "48.29"]
EMAIL_OK  = ["chandru.ms@srmist.edu.in", "ra2411026050028@srmist.edu.in", "a@b.com",
             "first_last@mail-server.org", "x1-y2@dept.univ.in"]
EMAIL_BAD = ["chandru@", "@srmist.edu.in", "a..b@x.com", "a@b.xyz", ".a@b.com", "a.@b.com",
             "a b@x.com", "a@-b.com", "a@b..com", "plain-text"]
PW_OK  = ["Chandru@2026", "Fla#Auto9mata", "Zz9!zzzz", "Abcdefg1!", "S3cure&Pass_ok"[:-3] + "k!"]
PW_BAD = ["chandru@2026", "CHANDRU@2026", "Chandru2026", "Chandru@abcd", "Ab1!", "Abcdefg1!" + "x" * 8,
          "Chandru @2026", "Chandru_2026"]
