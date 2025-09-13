import streamlit as st   # For web app UI
import csv              # For reading/writing csv files
from datetime import datetime  # For dates and times

# Set up browser tab and app layout 
st.set_page_config(
    page_title="Launchpad",   # Title on browser tab
    page_icon="🚀",           # Favicon
    layout="centered"         # Center content (looks cleaner)
)

#CSS: Hero band + overlapping white panel
st.markdown(
    """
    <style>
    /* Gradient background */ 
        .stApp {
            background: linear-gradient(180deg, #f0f6ff 0%, #ffffff 85%);
        }
      :root{
        --blue:#0a3666;
        --ink:#1e2433;
        --muted:#5b6472;
        --line:#e8edf4;
        --pill:#f1f5ff;
      }

      /* Hero background */
      .hero {
        background: var(--blue);
        padding: 32px 16px 120px;   /* bottom padding ensures white card can overlap */
      }

      /* Brand row (centered LaunchPad) */
      .brandbar {
        max-width: 1080px; margin: 0 auto;
        display:flex; align-items:center; justify-content:center; gap:10px;
        color:#fff; font-weight:800; font-size:24px;
      }

      /* White card that overlaps hero band */
      .content-card {
        max-width: 960px;
        margin: -90px auto 40px;  /* negative margin pulls it upward */
        background:#fff;
        border-radius: 18px;
        box-shadow: 0 16px 32px rgba(0,0,0,.18);
        padding: 28px 30px 34px;
      }

      /* Headline text */
      .headline {
        text-align:center; color: var(--ink);
        font-size: 28px; font-weight: 800;
        margin: 4px 0 18px;
      }

      /* Quick search chips  */
      .chips { display:flex; gap:8px; flex-wrap:wrap; justify-content:center; margin: 6px 0 14px;}
      .chip {
        background: var(--pill); border:1px solid #dbe7ff; color:#2d3a55;
        padding:6px 10px; border-radius:999px; font-size:13px; cursor:pointer;
      }
      .chip:hover{ filter:brightness(.97); }

      /* Streamlit input: make it more "Google-ish" */
      .stTextInput>div>div>input{
        padding: 0.95rem 1.05rem; border-radius: 12px; font-size: 16px;
      }

      /* Result card styling */
      .job-card{
        border:1px solid var(--line); border-radius:14px;
        box-shadow: 0 3px 10px rgba(0,0,0,.06);
        padding:16px 18px; margin:12px auto; max-width:820px; background:#fff;
      }
      .job-title{ font-size:18px; font-weight:800; color:var(--ink); margin:0 0 2px;}
      .job-meta{ color:var(--muted); margin:0 0 8px; }

      /* Small info badges (experience, posted date, source) */
      .pills{ display:flex; gap:8px; flex-wrap:wrap; margin: 6px 0 10px;}
      .pill{ font-size:12px; background:#f7f9fd; border:1px solid var(--line); padding:4px 8px; border-radius:999px; color:#344; }
      .pill.good{ background:#e6fff6; border-color:#bff2e3; color:#0a6; }

      /* Apply button */
      .apply{
        display:inline-block; margin-top:4px; font-weight:700; text-decoration:none;
        background:#111827; color:#fff; padding:8px 12px; border-radius:10px;
      }
      .apply:hover{ filter:brightness(1.05); }

      /* Empty state box */
      .empty{
        text-align:center; padding:18px; border:1px dashed var(--line);
        border-radius:12px; background:#f9fbff; color:#2b3342;
      }

      /* Footer */
      .foot{
        text-align:center; color:#dbe7ff; font-size:12px; opacity:.9; padding: 16px 0 22px;
      }
    </style>

    <!-- Hero band -->
    <div class="hero">
      <div class="brandbar">
        <img src="https://emojicdn.elk.sh/🚀" width="26" alt="rocket"/> <!--would use logo after emoji used for hackathon timeframe--!>
        <span>LaunchPad</span>
      </div>
      <!-- Decorative white rounded rectangle under header -->
      <div style="
          max-width:900px; margin:18px auto 0; height:54px; background:#fff;
          border-radius:16px; box-shadow:0 8px 24px rgba(0,0,0,.22);">
      </div>
    </div>

    <!-- Main content card -->
    <div class="content-card">
      <div class="headline">Find real entry-level roles faster</div>
      <div class="chips">
        <span class="chip" onclick="window.parent.postMessage({type:'chip','q':'Junior Developer'},'*')">Junior Developer</span>
        <span class="chip" onclick="window.parent.postMessage({type:'chip','q':'Project Coordinator'},'*')">Project Coordinator</span>
        <span class="chip" onclick="window.parent.postMessage({type:'chip','q':'Data Analyst'},'*')">Data Analyst</span>
        <span class="chip" onclick="window.parent.postMessage({type:'chip','q':'Marketing Coordinator'},'*')">Marketing Coordinator</span>
      </div>
    """,
    unsafe_allow_html=True,
)

#Search bar 
query = st.text_input(
    "🔎 Search Job Title",  # Label 
    placeholder="Try: Junior Developer, Project Coordinator, Data Analyst",
).strip()

# Allow quick chips to fill the input box
st.markdown(
    """
    <script>
      window.addEventListener('message', (e)=>{
        if(e?.data?.type === 'chip'){
          const boxes = parent.document.querySelectorAll('input[type="text"]');
          if(boxes && boxes.length){ boxes[0].value = e.data.q; boxes[0].dispatchEvent(new Event('input', {bubbles:true})); }
        }
      }, false);
    </script>
    """,
    unsafe_allow_html=True
)

#  Load jobs from CSV file
def load_jobs(path="data/jobs.csv"):
    """Reads jobs.csv and cleans data (years_required → int, posted_at → datetime)."""
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            # Convert years_required from string → int 
            try:
                r["years_required"] = int(r.get("years_required", "99"))
            except ValueError:
                r["years_required"] = 99

            # Convert posted_at string → datetime 
            posted = r.get("posted_at", "")
            try:
                r["posted_at"] = datetime.fromisoformat(posted)
            except Exception:
                r["posted_at"] = None

            rows.append(r)
    return rows

jobs = load_jobs()

#Filter + display results 
if not query:
    st.caption("Start by searching a job title.")  # Empty state helper
else:
    # 1) Filter to true entry-level (0–2 yrs)
    filtered = [r for r in jobs if r["years_required"] <= 2]

    # 2) Keyword match on title (case-insensitive)
    q = query.lower()
    filtered = [r for r in filtered if q in r["title"].lower()]

    # 3) Sort newest → oldest
    filtered.sort(key=lambda r: r["posted_at"] or datetime.min, reverse=True)

    # Show number of results
    st.caption(f"Showing {len(filtered)} role(s)")

    if not filtered:
        # Styled empty state
        st.markdown(
            "<div class='empty'>No true entry-level roles found — try another title or click a quick chip above.</div>",
            unsafe_allow_html=True,
        )
    else:
        # Render each job card
        for r in filtered:
            posted = r["posted_at"].date().isoformat() if r["posted_at"] else "—"
            source = r.get("source") or "—"
            yrs = r["years_required"]

            st.markdown(
                f"""
                <div class="job-card">
                  <div class="job-title">{r['title']}</div>
                  <div class="job-meta"><b>{r['company']}</b> · {r['location']}</div>

                  <div class="pills">
                    <span class="pill good">0–2 yrs</span>
                    <span class="pill">Posted {posted}</span>
                    <span class="pill">Source: {source}</span>
                  </div>

                  <a class="apply" href="{r['apply_url']}" target="_blank" rel="noopener">Apply</a>
                </div>
                """,
                unsafe_allow_html=True,
            )

#Footer 
st.markdown("</div>", unsafe_allow_html=True)  # Close .content-card

st.markdown(
    """
    <div class="foot">Built for Zero Boundaries — Social Good · 0–2 yrs only</div>
    """,
    unsafe_allow_html=True,
)
