# Tennis deep analytical question bank — AskTennis / MCP schema (Volume 2)

This bank is **new relative to** `TENNIS_ANALYTICAL_QUESTIONS.md`, `TENNIS_ANALYTICAL_QUESTIONS_MCP.md`, and `ANALYTICAL_QUESTIONS_CURATED.md`. Questions assume the AskTennis data model: split tour tables (`atp_matches`, `wta_matches`, `atp_players`, `wta_players`, `atp_rankings`, `wta_rankings`), optional unified `matches`, `doubles_matches`, views such as `matches_with_full_info` / `matches_with_rankings`, and MCP charting (`atp_mcp_*`, `wta_mcp_*`) joined via `match_id`, `linked_match_id`, and related aggregate stat subtables (~18 per tour) described in project docs.

**Intent:** SQL- and analytics-shaped questions that cite **concrete fields** (`w_1stIn`, `w_bpFaced`, `tourney_level`, `winner_entry`, `minutes`, `best_of`, `match_status`, MCP serve/return/rally tables, etc.) rather than generic tennis trivia.

---

## 1. Match-level derived metrics (`atp_matches`, `wta_matches`)

_Field-explicit rate algebra, rank gaps, demographics slices._

1. Using `atp_matches` with non-null `winner_rank` and `loser_rank`, which players maximize the median upset margin `(loser_rank - winner_rank)` across wins with ≥40 qualifying victories?
2. For each `event_year` on `wta_matches`, compute the correlation between `minutes` and `ABS(winner_rank - loser_rank)`; which five years show the strongest positive correlation and why might scheduling explain it?
3. Among ATP rows whose `tourney_level` encodes Grand Slams, what fraction of wins satisfy `w_svpt > l_svpt` while `w_ace < l_ace`, and how does that fraction differ by `surface`?
4. On grass `wta_matches`, rank players by mean `w_bpFaced / NULLIF(w_svpt,0)` in matches they won; require ≥25 grass wins—who survives repeated return pressure?
5. List `atp_matches` where `l_bpFaced >= 5` and break-save rate exceeds the winner's: `l_bpSaved/NULLIF(l_bpFaced,0) > w_bpSaved/NULLIF(w_bpFaced,0)`.
6. Per `winner_id` in ATP, compute share of wins with `w_df = 0`; list names in the top decile among players with ≥200 wins.
7. From `wta_matches` loser columns, which players most often post `l_1stWon/NULLIF(l_1stIn,0) > 0.65` while losing (≥40 such losses)?
8. For each `loser_id`, compare loser serve efficiency `(l_1stWon+l_2ndWon)/NULLIF(l_svpt,0)` to the winner’s on losses; who is most competitive in defeat (≥50 losses)?
9. Split `atp_matches` by decade; for each, evaluate `(mean(w_ace - l_ace) in mapped finals) minus (mean(w_ace - l_ace) in mapped first rounds)`—which decade shows the largest positive gap?
10. Count `wta_matches` with `w_df >= 10` AND `l_df >= 10`, grouped by `tourney_name`—which events accumulate the most extreme double-fault duals?
11. Among ATP `best_of = 5` rows, contrast `minutes` distributions for score patterns implying four sets vs five sets.
12. Among ATP winners with ≥100 wins, which `winner_ioc` groups have the highest mean `winner_ht`, and do they also show higher `w_ace/NULLIF(w_svpt,0)`?
13. For semi-final–equivalent `round` strings, compare mean `winner_age - loser_age` in upsets (`loser_rank < winner_rank`) vs chalk on each `surface`.
14. On hard `wta_matches`, measure upset rate in matches opposing `winner_hand` L to R combinations vs R-R baselines.
15. Trend by `event_year` the share of ATP matches with net aggressive serving: `(w_ace+l_ace) - (w_df+l_df) > 10`.
16. Which `tourney_name` values show the widest IQR of `minutes` among ATP hard-court finals staying best-of-three?
17. Find WTA players whose clay win% rises by >15 points when `loser_rank <=20` vs `>20`, each bucket needing ≥60 clay matches.
18. Rank WTA players by mean `l_bpFaced` in their wins (they are `winner_id`) with ≥30 wins—who wins while inviting pressure on serve?
19. When both seeds exist, compute average upset frequency if the higher seed also holds the numerically better pre-match `winner_rank`/`loser_rank` alignment.
20. Bucket `match_status` for ATP and relate retirement prevalence to partial `score` leadership heuristically—surface-level QA summary.
21. Within each `surface`, bin ATP winners by `winner_ht` decile; describe monotonicity of `w_1stIn/NULLIF(w_svpt,0)` across bins.
22. Which ATP winners most frequently win while their opponent faced `l_bpFaced >=10` yet the winner’s return breaks stayed at 0 (infer carefully from `l_bpFaced`, `w_bpFaced` symmetry)?
23. Month-level `wta_matches`: where is mean `(w_ace+l_ace)` minimized?
24. Proxy rally grind with `minutes / NULLIF(w_ace+l_ace,0)`; rank clay tournaments by median grind index.
25. Per `tourney_level`, compare mean `winner_rank_points - loser_rank_points` for upsets vs non-upsets on ATP.
26. Find ATP hard-court players whose five-year rolling means of `w_1stWon/NULLIF(w_1stIn,0)` never decrease across career.
27. When both heights exist and differ by >15 cm, how often does the taller player win in ATP?
28. Distribution of `(loser_rank - winner_rank)` for `wta_matches` with `winner_age <21` and `loser_rank<=50`.
29. For winners aged ≥34 with ≥25 wins on hard, clay, grass each, rank surfaces by win rate—late-career surface affinity.
30. Which WTA seasons show the largest gap between mean `w_df` in three-set wins vs straight-set wins?
31. Find players with ≥25 losses where `l_ace >= w_ace` and `l_1stIn/NULLIF(l_svpt,0) > 0.65` simultaneously.
32. Tertile `w_svpt - w_1stIn` exposure for winners; compare distributions of `w_df/NULLIF(w_svpt,0)` across tertiles.
33. Cross-tab `winner_entry` with upset indicator—largest raw upset count entry type in ATP main draws?
34. Estimate frequency both athletes exceed tour-wide median first-serve-in for their serving role in the same row.
35. Per `event_year`, Gini coefficient over per-match `(w_ace+l_ace)`—serving concentration through time.
36. Rank IOC codes by mean height among each code’s top-10 match winners by win count in ATP.
37. Longest calendar-ordered ATP win streak where opponents never exceed `l_bpFaced` of 2 while the focal player serves—approximate hold dominance.
38. Contrast early-round vs QF+ `minutes` on hard tournaments whose names suggest indoor play.
39. For `wta_matches` with `loser_rank<=10`, histogram `winner_rank` bands 1–25, 26–75, 76+.
40. Grass WTA with ≥40 wins: bucket-test association between `winner_ht` decile and `w_ace/NULLIF(w_svpt,0)`.
41. Per slam `tourney_name`, estimate top-seed vs second-seed finals conversion differences across decades.
42. Upset probability by half-decade age buckets; compare Masters-like `tourney_level` to 250-level rows.
43. Pre/post-2000 ATP hard courts: mean return-side efficiency proxy `(l_1stWon+l_2ndWon)/NULLIF(l_svpt,0)` for winners.
44. Rank players by median `minutes` in wins minus median in losses with ≥150 recorded decisions.
45. Calendar quarter aggregation of ATP five-setters share among `best_of=5` rows.
46. Interaction table of `(winner_hand, loser_hand)` vs mean total aces in ATP—beyond win rates.
47. Summarize `match_status` vs `surface`—which surfaces retire most?
48. Coefficient of variation of `w_1stIn/NULLIF(w_svpt,0)` across ATP wins—≥100 wins.
49. ATP finals where both sides’ `*_bpFaced` exceed the surface 90th percentile—grind index.
50. Rate of taller-player losses despite better `winner_rank`/`loser_rank` alignment on WTA.
51. When `winner_rank_points` and `loser_rank_points` are both present, find matches with minimal point gap but lower-ranked winner.

## 2. Weekly rankings (`atp_rankings`, `wta_rankings`)

_Velocity, churn, joins to matches, integrity checks._

52. Join `atp_rankings`/`wta_rankings` to players: largest legitimate week-over-week points jump for a single player id.
53. Longest WTA streak of consecutive weeks ranked 2–10 without achieving rank 1.
54. Players whose rank swings >200 in one calendar year while touching top 50.
55. Mean absolute discrepancy between closest pre-event ranking join and embedded `winner_rank` for 10k sampled ATP matches.
56. Among former ATP #1s, greatest share of career weeks spent ranked 15–40.
57. Year-end histogram of points at rank 50: ATP vs WTA contrast for the same calendar years.
58. WTA teenagers whose month-by-month best rank strictly improves through a calendar year.
59. Weeks where ATP points gap ranks 1–10 is <10% of leader points—compressed eras.
60. Youngest age at first top-100 week after joining the player birth date field from `atp_players` or `wta_players` (exact column name per deployment DDL).
61. Count distinct top-100 players per WTA `ranking_date`; 1990s mean vs 2010s mean.
62. After ≥52 missing ranking weeks, typical point rebound slope in first 12 back.
63. Duplicate-detection query for identical player/date with conflicting points.
64. Weekly rank variance over trailing 8 observations: <21 vs >28 years old.
65. Weeks with compatriot WTA #1 and #2 simultaneously.
66. Skewness proxy for ATP points at rank 50 by year via SQL moments.
67. Largest improvement from pre-30 peak rank to post-30 peak rank.
68. Mean weeks between separate top-20 stints for players with >40% clay-weighted schedules.
69. Careers where stddev(rank) > mean abs delta rank—noisy movers.
70. Per-year median rank of second-best player per IOC in top 200 WTA.
71. Fastest fall from top 10 to beyond 200 among players with fewer than 80 intervening weeks logged.
72. Distinct IOC count in ATP top 200 by `ranking_date` trend line slope 1990–2024.
73. Steepest weekly points drop not followed by four-week idle gap—false injury proxy.
74. Annual Gini on ranking points mass top 1% ATP vs WTA.
75. Weeks where ATP #1 IOC equals WTA #1 IOC.
76. Lag-1 autocorrelation of rank for players with 104+ contiguous weekly rows.
77. Longest post-#1 ATP span spent continuously below rank 100.
78. Fastest points-per-week ascent using first 52 ranking rows only.
79. Systematic mismatch direction when `winner_rank_points` exceeds joined points by >5%.
80. ‘Bubble weeks’ with many players within 50 points between ranks 45–55.
81. Most career weeks ranked 11–20 in WTA without hitting top 10.
82. Correlation of October points with next January points—year boundary carry.
83. Countries by count of distinct ATP players ever reaching top 50.
84. Players in `atp_rankings` before first `atp_matches` appearance—pipeline QA.
85. Longest uninterrupted ATP weeks in top 5 without hitting #1.
86. Players oscillating top50↔outside150 in ≥5 distinct years.
87. Decadal mean points at ATP rank 100—depth inflation narrative.
88. Post-slam ranking rows where both finalists drop points maintain rank order—defensive success stories.
89. Weekly top-100 entry minus exit counts—churn intensity by year.
90. WTA match-rich players with sparse ranking history—ingest gap detection.
91. Rank volatility difference for players born January vs December, age-aligned.
92. Total weeks ranked without ever reaching top 20—rank the longest.
93. Probability moving from rank 50–75 to top 20 within 52 weeks—cohort SQL survival approximation.
94. Peak weekly points above historical 90th percentile but never rank 1—ceiling club.

## 3. Events & schedule (`tourney_name`, `tourney_level`, `round`)

_Balance, fatigue, field strength, metadata heuristics._

95. Shannon entropy of distinct champions per `tourney_level` and year—unpredictability index.
96. Events with highest repeat finalist pair density relative to finals count.
97. #1 seed first-round loss rate when seeds populated.
98. Upset rate tournaments following back-to-back same-surface events vs spaced events (date-gap heuristic).
99. `winner_entry` pathways vs QF+ rate at ATP 500 vs 1000 analogs.
100. Events where qualifiers outperform wildcards on expected wins from entry metadata.
101. Mean finals `minutes` by `surface` within Masters-like `tourney_level`.
102. Finals length when both semis were top-decile long vs not.
103. Lowest retirement-rate tournaments using `match_status`.
104. Heuristic home IOC boost parsing host tokens from `tourney_name` vs neutral events—document caveats.
105. Smallest summed finalist rank slams vs largest—parity extremes.
106. Two-set vs three-set WTA matches ace intensity at same `tourney_level`.
107. Back-to-back distinct hard `tourney_name` titles within 14 days per player.
108. Indoor keyword in `tourney_name` vs ace rate conditional on hard `surface`.
109. Years with most distinct tournaments whose finals were both `winner_rank` and `loser_rank` ≤5.
110. Linear trend of champion rank at each ATP 250 analog 2005–2024.
111. Events whose finals upset rate beats global finals upset rate by >10pp.
112. Count slam defending champion R1 exits by year heuristics.
113. `score` strings containing '7-6' density leaderboard for `tourney_name`.
114. Weekly median WTA vs ATP `minutes` bucketed by ISO week—calendar load.
115. Cup-style `tourney_name` rows that look like tour-level singles stats—schema coherence audit.
116. Two-event hard swings: week2 win% minus week1 win% >25 points for repeat entrants.
117. Correlation of pre-tournament 20-match win% with seed overperformance.
118. Skewness of finalist `winner_age` by recurring event.
119. Frequency both top-4 seeds reach semis when all four seeds exist.
120. Year-to-year variance of champion rank for each `tourney_name`—volatility ranking.
121. Lefty finalist rate by event vs tour baseline.
122. Olympic-year global ATP match-count deficit vs ±1 year mean.
123. Upset hazard R16 vs QF controlling mean rank-gap bins.
124. `loser_seed` null rate curve across `tourney_level`.
125. Tournaments ranked by mean winner `w_bpSaved/NULLIF(w_bpFaced,0)`.
126. Same-season prior meetings count for finalists via self joins on player ids.
127. Winner IOC entropy per event-year—international spread.
128. Surface specialty index extremes attracted to which events?
129. Correlated upset rates between same-month tournament pairs.
130. Early vs late calendar double faults per serve point binning.
131. ATP finals tiebreak-string density vs baseline.
132. Next-event win% after three-set loss vs straight loss for same player same surface.
133. Qualifier QF+ rate multiplier vs tour mean by event.
134. Same-nation women’s finals rate vs men’s by year.
135. Share of slam matches where both players’ ranks ≤20 when populated.
136. Median first-round rank-gap vs finals rank-gap by slam name.
137. Overload weeks: matches involving top-10 exceed μ+2σ.
138. Seeded loss rate conditional on winner leading `w_1stWon` battle—parse carefully.
139. Women’s R32 median minutes vs men’s at aligned levels when data overlap.
140. Event-level ace-rate excess over global mean as pace proxy for analysts lacking CPI.

## 4. `doubles_matches` & format comparison

_Teams, coverage, mirrored singles contrasts._

141. Doubles partnership churn: mean distinct partners per player-year for active doubles competitors.
142. Repeat champion pair rate by doubles `tourney_name`.
143. Doubles vs singles `minutes` where tournament keys align.
144. Highest win% doubles teams with ≥25 rows—canonicalize player order.
145. IOC concentration doubles finals vs singles finals yearly.
146. Most dominant `score` margins in doubles data.
147. Doubles retirement rates by `surface` if `match_status` mirrored.
148. Partnerships improving win% monotonically across season thirds.
149. Doubles-heavy players with thin singles rows—specialist detector.
150. Handedness mix on winning teams if joinable.
151. Doubles row volume slope by year—coverage curve.
152. Age-gap distribution winners vs losers in doubles when ages exist.
153. IOC leaderboard doubles titles count.
154. Doubles upsets using team rank fields when present.
155. Partnership lift metric AB vs A with others.
156. Indoor keyword doubles ace differential.
157. Longest doubles win streak per canonical pair string.
158. Super tiebreak prevalence in `score` if denoted.
159. Men vs women doubles pace proxies when sex-segregated tables exist.
160. Tournaments overrepresented in doubles vs singles row ratio.
161. Doubles walkovers by month.
162. Players with 500+ singles wins and top-20 doubles win totals same window.
163. Correlation doubles win% with singles rank nearest week if joinable.
164. Null-rate histogram doubles columns by year—QA.
165. Opponent diversity index top doubles teams.
166. Partnerships >80% win and 40+ matches.
167. First-time team vs established team win% delta.
168. Three-set doubles score density by event.
169. Doubles losses despite higher summed team rank when ranks exist.
170. DF distribution doubles vs singles same event-year.
171. Top-20 doubles team turnover rate year to year if definable.
172. Anomalous doubles score tokens—typo candidates.
173. National team events doubles overlap with regular tour same pair?
174. Doubles matches same calendar day per player—scheduling plausibility.

## 5. MCP linkage, coverage, reconciliation

_`linked_match_id`, `atp_mcp_*`, `wta_mcp_*`, QA vs box scores._

175. Share of `atp_mcp_matches` lacking joinable `linked_match_id` to `atp_matches`.
176. `minutes` distribution ATP: MCP-linked vs unlinked rows.
177. Player-level ratio MCP wins / all ATP wins—bias toward elites?
178. MCP coverage rate finals vs R32 by counting distinct keys.
179. Do MCP-linked ATP matches skew longer `minutes` than unlinked within same tournament-year cell?
180. Surface mix MCP WTA vs MCP ATP match counts—imbalance metric.
181. Events ranked by % of main-draw singles with MCP linkage.
182. Correlation career ATP wins with count of MCP rows containing player id.
183. Fastest `event_year` growth in new MCP rows—adoption curve.
184. For linked matches, mean absolute error between sum of MCP-aggregated aces (if rolled up) and `w_ace+l_ace`—if subtables allow.
185. Linked matches: compare MCP point counts derived from `atp_mcp_points` to implied points from `score`—discrepancy tails.
186. Lefty share MCP ATP vs all ATP—representation test.
187. MCP inclusion logistic on indicator both players top 50 at match ranks.
188. Duplicate rate on (`match_id`, point sequence) if columns exist.
189. Mean points per match `wta_mcp_points` vs `atp_mcp_points`.
190. Integrity failures: MCP winner disagrees with `atp_matches` winner post join.
191. Rally length quantiles from MCP rally tables by `surface` for players with ≥30 charted matches.
192. SNV attempt rate grass vs clay MCP aggregates.
193. Rank players by `(winners - unforced_errors)` surplus in MCP shot tables with point minimums.
194. Ad-court vs deuce-court serve win% from MCP key-point or direction splits.
195. Return depth bucket win rates aggregated for big servers (≥10 aces same match).
196. Forehand direction entropy from MCP shot-direction fields.
197. Net approach win% with ≥100 approaches filter using net tables.
198. ATP vs WTA mean rally length field from MCP overview tables.
199. Matches where MCP first-serve % differs >15 points from `w_1stIn/NULLIF(w_svpt,0)` in `atp_matches` for same player side.
200. Share of five-setters fully charted vs partially using point count completeness heuristics.
201. Events by mean MCP points logged per match—chartist effort proxy.
202. Systematic over/under of aces MCP vs box score by player career.
203. Indoor hard MCP: wide vs body serve win rates from direction tables.
204. Serve-direction influence metrics: marginal gain from wide deuce serves for top 20 servers.
205. Shallow return share after opponent ace prior point—conditional table.
206. Key-points split: game-point save rate vs ordinary service points.
207. Forced error creation rate leaders clay MCP shot outcomes.
208. Longest MCP logged rally and its tournament/surface attribution.
209. Forced vs unforced error mix conditional on deep vs shallow return tags.
210. Split-half stability of MCP clutch metrics per player.
211. Approach-shot success ATP vs WTA MCP if tagged.
212. Correlation MCP mean rally length with `minutes` for linked matches.
213. Round-level MCP coverage clustering suggesting selective charting.
214. Player deltas between MCP break-point table performance and overall return points won.
215. Bagel set frequency MCP linked vs population.
216. Heuristic inconsistency between MCP point sequence and game-wise `score` progression—QA sampling.
217. MCP coverage before vs after 2015 by match share—technology/staffing story.
218. Opponent-specific MCP sample tilt: concentration of charted matches vs handful of rivals.
219. Bias in career second-serve win% estimates using only MCP-linked matches vs all matches.
220. MCP clutch serve performance vs lefty opponents specifically.
221. Cross-table contradictions same match overview vs serve basics.
222. Titles won vs MCP row count correlation—celebrity charting bias?
223. Coefficient of variation of points per charted match for players with >50 MCP matches.
224. Which MCP subtables (names per deployment DDL) are most null-heavy—automated schema scan question.
225. WITH-clause skeleton auditing serve efficiency by re-aggregating MCP basics joined on `linked_match_id`.

## 6. Granular MCP hypotheses

_Stat-subtable comparisons; explicitly comparative—not generic ‘who serves best’._

226. In ATP MCP charted matches, analyze: pressure index from key-points tables at 15-40 down—compare to baseline serve points won; largest negative gap leaders.
227. In WTA MCP charted matches, analyze: serve-direction asymmetry: deuce-wide vs ad-wide win% when score ahead vs behind.
228. In ATP MCP charted matches, analyze: return depth: marginal win prob deep vs shallow after opponent prior ace.
229. In WTA MCP charted matches, analyze: forehand winner rate conditional on rally length ≥5 in shot tables.
230. In ATP MCP charted matches, analyze: high net win% but low net frequency—selective net efficiency.
231. In WTA MCP charted matches, analyze: SNV: point win% after first-serve SNV vs second-serve SNV attempts.
232. In ATP MCP charted matches, analyze: down-the-line backhand winner share on break points.
233. In WTA MCP charted matches, analyze: unforced error rate 1–3 shot rallies vs ≥9 for same player.
234. In ATP MCP charted matches, analyze: documented return games won vs deep-return share correlation.
235. In WTA MCP charted matches, analyze: performance on set points vs match points—gap leaderboard.
236. In ATP MCP charted matches, analyze: opponent adjustment cost when rotating serve locations—influence metrics.
237. In WTA MCP charted matches, analyze: break conversion modeled as deep-return share × opponent second-serve vulnerability interaction.
238. In ATP MCP charted matches, analyze: forced-error-to-winner ratio on tagged defensive shots in long rallies.
239. In WTA MCP charted matches, analyze: net approaches per set vs surface from net tables.
240. In ATP MCP charted matches, analyze: serve/break split: serving to stay in match vs serving with lead.
241. In WTA MCP charted matches, analyze: Shannon entropy of second-serve location at deuce.
242. In ATP MCP charted matches, analyze: share of points won in odd- vs even-stroke rallies—tactical signature.
243. In WTA MCP charted matches, analyze: returning after losing prior point on own serve—depth performance drop.
244. In ATP MCP charted matches, analyze: slice vs topspin backhand usage rates on clay MCP tags.
245. In WTA MCP charted matches, analyze: game-point vs regular-point buckets clutch delta.
246. In ATP MCP charted matches, analyze: variance of charted first-serve % weighted by opponent strength.
247. In WTA MCP charted matches, analyze: immediate aggressive returns (0–1 shot) after opponent second serve.
248. In ATP MCP charted matches, analyze: set-deciding points mix of winners vs errors—outcome table QA.
249. In WTA MCP charted matches, analyze: inside-out forehand directional skew ad vs deuce court.
250. In ATP MCP charted matches, analyze: body-serve share vs opponent height advantage >15 cm.
251. In WTA MCP charted matches, analyze: double fault on second serve following first-serve fault—conditional hazard vs baseline.
252. In ATP MCP charted matches, analyze: second-serve win% only—compare ATP vs WTA MCP cohorts on hard.
253. In WTA MCP charted matches, analyze: deep return share down break point vs up break point.
254. In ATP MCP charted matches, analyze: P(long rally | prior long rally)—persistence.
255. In WTA MCP charted matches, analyze: performance 30–30 vs 40-AD games aggregated.
256. In ATP MCP charted matches, analyze: wide serve share jump on second serve vs first.
257. In WTA MCP charted matches, analyze: drop shot attempt rate after rally >6 prior shot.
258. In ATP MCP charted matches, analyze: players in overview missing shot-direction rows—coverage loss audit.
259. In WTA MCP charted matches, analyze: lefty servers × deep return win interaction.
260. In ATP MCP charted matches, analyze: winners per charted minute vs errors per minute.
261. In WTA MCP charted matches, analyze: net success when approach follows inside-out setup vs down-the-line setup.
262. In ATP MCP charted matches, analyze: wide ad-court serves: induced opponent error rate ATP vs WTA same surface.
263. In WTA MCP charted matches, analyze: first-serve % drop magnitude serving at match point down.
264. In ATP MCP charted matches, analyze: totals reconciliation overview vs summed point table.
265. In WTA MCP charted matches, analyze: backhand winner rate decay beyond rally length 7.
266. In ATP MCP charted matches, analyze: short return then immediate winner conceded rate.
267. In WTA MCP charted matches, analyze: tiebreak-only key-point metrics vs outside tiebreaks.
268. In ATP MCP charted matches, analyze: forced error share monotone across rally deciles.
269. In WTA MCP charted matches, analyze: SNV success indoor vs outdoor hard within MCP.
270. In ATP MCP charted matches, analyze: T-serve share uplift under break point.
271. In WTA MCP charted matches, analyze: after deep return error, next point win probability.
272. In ATP MCP charted matches, analyze: second-serve aces encoded in point strings—frequency leaders.
273. In WTA MCP charted matches, analyze: angular vs central winners from direction tags.
274. In ATP MCP charted matches, analyze: serve-volley failure modes: volley UE vs pass winner counts.
275. In WTA MCP charted matches, analyze: split sample >30 charted matches each player before direction win% leaderboard filtering noise.

## 7. Methods, bias, robustness

_Adjustments for minutes, shrinkage, coverage bias, era slicing._

276. Normalize ace intensity by `minutes` before era comparisons—decade with highest aces/hour.
277. Efficiency frontier: high ATP win% with below-median serves attempted per match.
278. Empirical Bayes shrinkage on break-point conversion with tour prior for juniors with <200 returns.
279. Sensitivity of ‘upset kings’ leaderboard to imputing missing `loser_rank` via prior Monday ranking join.
280. Intercontinental schedule flips: consecutive distinct `tourney_name` clusters without geodesic data—proxy via name entropy jump.
281. Multicollinearity diagnostics between `winner_ht`, ace rate, first-serve-in—SQL correlation matrix excerpt.
282. Winsorize `minutes` at 1% tails before surface A/B tests.
283. Z-score feature vectors from serve/return aggregates then kNN player similarity—conceptual SQL outputs.
284. Year-stability of rank-gap-conditioned upset indicators—split-half by season.
285. Autocorrelation of weekly match wins per player_id.
286. Female vs male upset rate sensitivity to match-date rank vs Monday rank joins.
287. Exact matched pairs on surface/round/year with flipped handedness combos—difference in means.
288. 2020 weekly match volume anomaly vs 2019 baseline.
289. Meta: minimum match threshold asymmetry WTA vs ATP affecting leaderboards—document Monte Carlo need.
290. Bootstrap CI concept for Big-Three era dominance ratio using SQL-aggregated season stats.
291. Cold streak: consecutive breaks conceded approximated via high `w_bpFaced` games—heuristic.
292. Marginal slam type contribution to year-end rank points when points table integrated.
293. Discriminative power of ‘higher ace player wins’ rule by surface.
294. False confidence warning: inferring style from `w_2ndWon/w_svpt` sans rally data.
295. Incremental R^2 narrative: MCP features vs box-score-only linear proxies for match outcome.
296. Stationarity test on global mean `w_1stIn/w_svpt` 50-year slices.
297. Effect of excluding qualifying mismatches on main-draw aggregates.
298. Which single stat differential best aligns with WTA three-set winners—SQL sweep.
299. `minutes` variance gender comparison best-of-three vs best-of-five comparable subsets.
300. Weeks-with-zero-matches count for active top-100 players by season—rest vs inactivity.
301. Anomaly: both players career-high rank same match row?
302. Cohort: debut post-2005 vs pre-1990 second-serve aggression trend.
303. Trailing 10-match std of serve stats vs next-match upset indicator—window functions.
304. Home IOC advantage restricted to Spanish/Latin American clay host name keywords—explicit list management.
305. Tour depth: unique top-100 winners per year vs mean slam champion rank.
306. Monthly global match volume seasonality around slams.
307. Win-share Gini across all players per year—long tail mass.
308. Ace-share Gini across players annually—tail dominance.
309. Clutch definition robustness: exclude first-serve misses from pressure buckets.
310. `winner_ht` completeness trend by decade.
311. Row-count reconciliation unified `matches` vs `atp_matches`+`wta_matches` if both exist.
312. `score` walkover pattern with non-null `minutes`—hygiene list.
313. Composite durability: five-set wins minus retirement losses as winner.
314. Leverage points influence on seedings if points known—Shapley-style omitted.
315. False negative rate guessing indoors without keyword flag.
316. Inverse probability weighting MCP rows to correct elite bias—outline estimator.
317. Rank correlation between tournament draw size and upset rate if `draw_size` present.

## 8. Demographics & representation

_Height, age, hand, IOC, career span—all column-anchored._

318. IOC × height quartile × break-save rate triple slice ATP winners.
319. January-born vs December-born seasonally adjusted via `winner_age` binning.
320. Late birth-month juniors WTA Q1 win% effects.
321. Lefty `winner_hand` return-split win% vs righty opponents on clay.
322. Tallest quartile WTA with above-median return aggression proxy.
323. Sub-175 cm ATP servers by `w_ace/svpt` among winners.
324. Age-gap >10 upset rate and ace differential moments.
325. Teenagers vs 35+ in WTA deciding-set frequency.
326. `winner_ht` missingness curve by decade and IOC.
327. Near duplicate `winner_name` different ids—join hazard count.
328. Annual share left-handed among top-100 match participants.
329. Lefties `w_bpSaved/NULLIF(w_bpFaced,0)` premium on clay?
330. Country clusters in baseline vs aggressive z-score space using box scores.
331. IOC switch mid-career detection via id’s `winner_ioc` transitions on match rows.
332. Month-over-month `w_df` jump outliers—proxy coaching change events.
333. Grass: players with negative height vs ace correlation among ≥50 wins.
334. Same player ages 18–22 vs 33–37 serve efficiency trajectory.
335. Pre-22 break rate vs top-20 opponents—early return metric.
336. Slam finalist mean age trend separated by tour.
337. Birth country vs representation country mismatches via `atp_players` fields if split.
338. Career span years between min and max match dates vs late-career DF slope.
339. ‘Journeyman geography’: distinct `tourney_name` countries visited median.
340. Opponent nationality entropy for cosmopolitan players.
341. Height × handedness grass interaction table.
342. First-year vs fifth-year serve stat means for long-tenure players.
343. Female aces per cm height ranking.
344. Oldest quartile players maintaining above-median `w_1stIn/w_svpt`.
345. Correlation `winner_age` with `minutes` in losses—fatigue curve.
346. Smallest demo buckets warning list for analysts (counts <20).
347. Eastern European IOC share swings in top-50 snapshots.
348. Pacific players’ clay-hard specialty index vs global.
349. African IOC match volume relative to historical tour expansion phases.
350. Island nations raw title counts without population proxy.
351. Doubles height advantage team sums if available.
352. Performance vs strictly older opponents controlling surface.
353. Left/right matchup rate trend 1980–2024.
354. ≥15-year careers with monotonic declining ace rate cohort.
355. Gendered coach bench not in data—do not query; instead height/hand coverage audit.
356. Representation of doubles birthdates completeness vs singles players table.
357. Sibling pairs same-last-name high frequency—duplicate risk for NLP-to-SQL.
358. Youngest finalists by `winner_age` where runner-up older by >10 years—structured list.
359. Players changing reported `winner_hand` across eras—data inconsistency hunt impossible—skip—replace with seed vs rank mismatch frequency.
360. Seed vs rank mismatch rate ATP when both fields populated.
361. Junior ITF not in schema—use `tourney_level` futures strings if present to study pro transition.
362. Collegiate keywords in `tourney_name` affecting age distributions—US college pipeline proxy.

## 9. Streaks, momentum, scheduling runs

_Ordered events, windows, droughts, anomalies._

363. Longest ATP calendar streak avoiding top-10 opponents in matches won sequencing.
364. Most finals reached without title among players with ≥5 finals.
365. Longest WTA streak of three-set wins.
366. Longest clay win streak without conceding a set via `score` parsing.
367. Five-loss streak immediately after holding #1 seed in prior event.
368. Win-loss alternation rate per player—oscillation metric.
369. ATP five-set win followed by loss within 7 days rate.
370. First match after clay→grass seasonal pivot: win% drop leaders.
371. Back-to-back distinct tournament title streak lengths.
372. Consecutive active weeks with ≥1 match played.
373. Longest top-30 streak implied by joins without hitting top 5.
374. MCP-only: longest stretch saving match points proxied from key-point tables—if available.
375. Loss streaks where each loss still has `l_ace > w_ace` from loser perspective adjustment.
376. Win streak difficulty: avg defeated rank vs prior 20-match baseline.
377. Final-set tiebreak appearance streak via `score`.
378. Longest indoor-hard unbeaten run.
379. Seasons alternating QF+ then R1 exits pattern mining.
380. Max consecutive R1 losses while ranked ≤30.
381. Ten-match win streak: elevation of rolling `w_1stIn` mean vs baseline.
382. Longest no-deciding-set-loss streak for player with many five-setters.
383. Decreasing `minutes` per round while still reaching final—fatigue efficiency paradox?
384. Doubles partnership break conditional on prior three losses.
385. Gap weeks between first and second career top-10 win.
386. Paradox run: multiple high BP-conversion losses in a row.
387. Longest straight-set hard streak WTA.
388. Single-season multiple distinct top-5 upsets by one underdog.
389. No double-bagel losses streak for veterans.
390. Consecutive calendar years with ≥1 title.
391. Entropy of set outcomes in consecutive three-setters.
392. Road vs neutral win streaks using IOC host heuristic.
393. Win streak with strictly increasing opponent rank difficulty.
394. Loss streak with monotonic decreasing ace totals.
395. Performance week after ATP Finals participation proxy tournament names.
396. Max rest days between consecutive matches for active players—schedule gaps.
397. Consecutive matches whose `score` contains multiple '7-6' tokens.
398. Weeks ranked top 5 with zero titles that season—odd leader.
399. Never lose when up two sets to love—five-set population.
400. Bounce-back win% after 6-0 set loss.
401. Clay streak with every match exceeding median tour `minutes` for clay.
402. Hard streak where every win includes a tiebreak set.
403. Doubles: reclaim title with different partner year-over-year.
404. Longest ace-less win streak among servers with overall high ace reputation—conditional slice.
405. Momentum: P(win next) after break-point-heavy win >90th percentile BP count.

## 10. Integrity, completeness, hygiene

_Rows analysts should filter or escalate before trusting aggregates._

406. Zero tolerance: `winner_id` = `loser_id` row count.
407. Negative `minutes` count and null `surface` rate by year.
408. Scores implying loser won more sets—frequency.
409. Duplicate composite key candidates `(tourney_name, round, winner_id, loser_id, tourney_date)`.
410. `winner_rank` null rate finals vs R128.
411. Homograph names different ids: top collision strings.
412. `best_of` inconsistent with number of set tokens in `score`.
413. `wta_matches` column-wise NULL heatmap ranks for imputation priority.
414. Physically implausible `w_ace` per `minutes` outliers list top 50.
415. `event_year` inconsistent with `tourney_date` year.
416. Matches missing both rank fields share.
417. Orphan MCP rows: no ATP match within ±1 day same players.
418. `draw_size` spikes suspicious batch years.
419. `tourney_level` inconsistent with known slam name token—manual checklist query.
420. Rank points jumps without intervening matches for a player anomaly.
421. Palindromic score typos heuristic failures count.
422. Aggregate sensitivity: include vs exclude `match_status` retire.
423. Seeds contradict ranks beyond protection threshold frequency.
424. Largest `winner_age - loser_age` teenager-won matches.
425. Birth year before 1950 yet first match after 2010— impossible rows.
426. `wta_matches` rows with ATP-only tour markers if cross contamination column exists.
427. Older years higher NULL rate for serve stats—quantify.
428. Very low `minutes` yet many games in `score`—inconsistency sampling.
429. Rankings zero points yet rank <400 prevalence.
430. Same-last-name sibling finals count heuristic.
431. MCP point indices reset mid-match duplicate streak detection.
432. Back-to-back rows reversed winner/loser identical stats—possible duplication.
433. Share of completed WTA rows with `w_svpt = 0`.
434. If `data_source` exists, rows by source for auditing.
435. Fuzzy duplicate `tourney_name` clusters needing canonicalization map.
436. Players with wins>0 and losses=0 count impossible unless single-match bug.
437. Max matches same player same `tourney_date`—scheduling plausibility.
438. `round` ordering inconsistent with encoded draw round progression.
439. Junior events mis-tagged as ATP main using `tourney_level` outliers.
440. Rank points exceed recorded historical max—typo shortlist.
441. Left-hand flag completeness ATP vs WTA.

## 11. Views, ops, & analytic engineering

_Joins to views, migration, limits, pruner QA—not trivia._

442. `matches_with_full_info`: compare aggregated ace rate vs raw `atp_matches` to validate view refresh cadence.
443. `matches_with_rankings`: measure extra join overhead value by upset classification accuracy gain vs embedded ranks only.
444. `player_rankings_history` materialization: detect gaps between weekly points and match dates exceeding 10 days.
445. Join view-provided handedness to MCP direction stats—does charting differ by known laterality?
446. Use `matches_with_rankings` to compute ‘scheduled rank’ vs ‘official Monday’ difference distribution.
447. Leverage view denormalized names to catch MCP player spelling variants inflating distinct counts.
448. Player age computed from view vs embedded `winner_age` mismatch sampling.
449. Rankings view: reconstruct continuous rank paths; count weeks interpolated vs observed.
450. If `matches` unified exists, split-label leakage check between tours.
451. Exposure of `winner_entry` in views—does cardinality match base table?
452. Historical matches_without_stats flag if exists—quantify missingness impact on Section 1 questions.
453. Cross-database: `tennis_data_with_mcp.db` DuckDB macros vs SQLite pragmas affecting duplicate detection queries.
454. Cloud SQL export row checksum compare to local DuckDB for MCP tables subset.
455. Point-level `wta_mcp_points` join to `wta_mcp_matches` on keys; verify referential integrity percentage.
456. Aggregate MCP per match from points vs pre-aggregated overview speed benchmark question—engineering KPI.
457. Large-result policy: default LIMIT 100 affects tail analytics—how to batch?
458. Disk cache keys including tour—risk of cross-tour contamination in API layer unrelated to SQL.
459. Prepared statement parameterization for ranking date BETWEEN filters—index usage explain plan checklist.
460. Partition-friendly filter on `event_year` for BigQuery migration thought experiment.
461. JSON `score` normalization UDF to extract set counts—test vectors from weird retirement strings.
462. Name search case folding: Turkish locale issues in `lower(full_name)` joins?
463. Unicode homoglyphs in Cyrillic names causing join explosions—frequency sampling.
464. Year-end championships detection via `tourney_level` + name—verify champion rank summary matches ATP site manually for one season.
465. Olympic tournament rows present? Count by `tourney_name` token ‘Olympic’.
466. Exhibition markers in `tourney_level` if any—exclude from official win streaks.
467. Team `ioc` in doubles vs singles consistency for dual players.
468. Time zone shift affecting `tourney_date` boundary duplications for Pacific events.
469. Hall-of-fame induction years absent—do not infer—note external merge requirement.
470. Prize money column absent—cannot answer purse questions—document negative capability.
471. Court speed CPI absent—use ace excess over tour mean per event as substitute correlation with analyst-supplied CPI CSV join.
472. UMPIRE/challenge data absent—avoid Hawkeye accuracy prompts.
473. Weather not stored—wind narrative disallowed—replace with indoor/outdoor keyword flag analysis.
474. Betting odds absent—calibration questions off limits—focus on closing line analog via ranks not possible—state explicitly in analyst notes.
475. Multi-database auth separation: ensure `query_history` never joins PII into tennis fact tables accidentally.
476. GDPR: player birthdates in rankings joins—flag fields for redaction in exports.
477. Rate limits on public API affecting long SQL generation—operational, not analytical.
478. LLM schema pruner false negatives: query mentions ‘inside-out’—does pruner include shot tables?
479. Keyword ‘MCP’ alone—schema pruner MCP table inclusion test harness list.
480. Regression suite: golden SQL for questions 1–5 in this file—CI idea.

## 12. Extended studies, joins, and meta-analytics

_Head-to-head construction, window metrics, MCP normalization, ops-adjacent checks—each item is distinct._

481. Self-join `atp_matches` on distinct player pairs swapping winner/loser roles: rank rival dyads by highest match count with win% nearest 50–50 among those with ≥18 meetings.
482. Compute head-to-head surface stratification for the single ATP dyad with the most total matches—hard vs clay vs grass win partitions.
483. Among WTA players with ≥100 wins, identify the subset whose loss column `l_bpFaced` distribution is heavier-tailed (higher p95) than their `w_bpFaced` distribution when winning.
484. Measure elasticity of `w_ace` to opponent `loser_ht` bin for ATP servers conditioned on same surface.
485. For each ATP slam, list years where mean finalist age (`winner_age`,`loser_age` average) exceeds tour-wide finals mean by >2.5 years.
486. Quantify frequency of ‘double bagel’ score patterns in WTA vs ATP using `score` token search.
487. Find tournaments where the champion’s `winner_rank` is worse than the median rank of all QF losers that year at the same event.
488. Estimate set-level competitiveness via count of ‘7-’ tokens in `score`; rank players by mean tiebreak set density in wins.
489. Identify ATP matches where `minutes` is in the top 1% for that `surface` but total aces `(w_ace+l_ace)` is in the bottom 20%—silent grind outliers.
490. Compare mean `w_2ndWon/NULLIF(w_svpt-w_1stIn,0)` for winners who also have `w_df=0` vs `w_df>0` on second serves.
491. Window function: assign each player’s rolling prior-50-match ace rate at each `tourney_date`; correlate rolling rate with upset indicator in next match.
492. Rank countries by σ-split: standard deviation of `winner_rank` among players from that IOC with ≥200 wins—depth vs star-concentration.
493. Identify ‘serve-only’ outlier wins: ATP rows with `w_ace - w_df` in top percentile while return proxy `(l_1stWon+l_2ndWon)/NULLIF(l_svpt,0)` also exceeds median.
494. Among women’s matches, fraction where winner height is lower but `w_ace > l_ace`—undersized server punch narrative.
495. Detect calendar ‘double booking’ candidates: same `winner_name` appearing as winner on two `tourney_date` values ≤1 day apart across events—data error versus fast surface logistics.
496. For MCP-linked ATP matches only, compare distribution of `w_bpFaced` in linked vs unlinked population same `tourney_level`.
497. Aggregate MCP shot tables: forehand vs backhand winner share difference for top 20 charted ATP players.
498. Using MCP return depth buckets, evaluate whether ‘deep return’ share rises when `loser_rank` ≤20 vs >20 for the server.
499. Join MCP key-points tables with `minutes` quartiles: is clutch serve performance lower in longest matches?
500. Identify WTA players whose MCP rally distributions skew longer than their tour-wide `minutes` per win would predict—style mismatch diagnostic.
501. Count distinct MCP chartists or source tags if present in MCP metadata columns—heterogeneity audit.
502. Player-season level: total `minutes` accumulated by rank-1 holder vs rank-10 holder—load inequality.
503. For players who switch primary `winner_ioc` representation, compare pre-switch vs post-switch upset win rates minimum 40 matches each side.
504. Quantify ‘protection ranking’ artifacts: high `winner_seed` with poor `winner_rank` simultaneous frequency.
505. Find ATP R16 matches where both athletes entered with `winner_rank` and `loser_rank` ≤8—late-stage top-heavy collisions rate by event.
506. Measure correlation between tournament-specific ace excess (event mean aces minus global) and share of matches going three sets in WTA.
507. List players with monotonic increase in `l_bpFaced` faced across career thirds while maintaining >55% win rate—rising pressure resilience.
508. Identify slams with highest rate of matches where loser taller and younger yet still loses—youth/height paradox slice.
509. Compute for each handedness the opponent-induced DF rate: mean `w_df` in losses where opponent is lefty vs righty.
510. Rank rounds (normalized) by median `(w_bpSaved+w_bpFaced)/(l_bpSaved+l_bpFaced)` ratio—return-dominated rounds vs serve-dominated.
511. Seasonal Elo surrogate without iterative Elo: compare trailing win% plus rank margin logistic to raw outcomes for backtesting curiosity.
512. Doubles: partnerships with highest ace rate per partner-height sum quartile.
513. Doubles: events where mean match `minutes` exceeds singles mean at same `tourney_name` when both exist.
514. Rankings: identify players with multiple separable peaks (local maxima in points time series) using SQL-friendly window comparisons.
515. Rankings: longest plateaus where rank unchanged for ≥8 consecutive weeks while points still positive—frozen rank periods.
516. Matches: frequency of ‘symmetric stats’ rows where `w_ace=l_ace` and `w_df=l_df` and ranks within 3—analyst tie-break curiosity.
517. Matches: distribution of rank-sum `winner_rank+loser_rank` for finals vs first rounds—quality of field progression.
518. MCP: compare error type totals in overview vs sum of point-level error tags—reconciliation tolerance study.
519. MCP: SNV success vs baseline serve+1 groundstroke points for same player sample—incremental value of net approach.
520. MCP: direction table—percentage of points in ad court decided by wide serve followed by error within two shots.
521. WTA vs ATP: same statistic `mean(w_1stWon)/mean(w_1stIn)` by surface using separate tables—format-driven gap table.
522. Age×surface heatmap of mean `w_df/NULLIF(w_svpt,0)` for winners—second-serve recklessness geography.
523. Height decile vs mean `l_2ndWon/NULLIF(l_svpt-l_1stIn,0)` when player is loser—returner second-serve punishment skill.
524. Identify ‘rank inversion’ weeks: player beats higher rank but weekly ranking join still shows lower points next Monday—delay effects.
525. Slam path difficulty proxy: average rank of defeated opponents for champion using recursive CTE or repeated joins—complexity leaderboard.
526. Upset chain depth: tournament where lowest-ranked champion had the highest cumulative rank-sum of victims—giant-killer path metric.
527. Fatigue omen: loss in match following one where `minutes` + previous week `minutes` > p95 tour sum—binary outcome model features.
528. Return-pressure resilience in defeat: highest mean `l_bpSaved` among three-set losses (`loser_id`) where the player reached a deciding set—high workload on opponent serve despite exit.
529. Serve meltdown metric: wins where `w_df > w_ace` but `w_bpSaved/NULLIF(w_bpFaced,0)` > 0.6—chaotic resilience.
530. Junior bridge: if qualifying `tourney_level` strings include ‘Futures’ or ‘Challenger’, map graduation velocity to first ATP main-draw win week lag.
531. Colocation analysis: tournaments sharing city name token—correlated champion rank distributions.
532. National team density: weeks with >30 matches where `winner_ioc` equals `loser_ioc`—domestic tour stretch flags.
533. Clock skew: `tourney_date` modulo 7 distribution by region proxy via `tourney_name` continent keyword—weekend start speculation.
534. Hawkeye proxy disallowed: instead measure challenge-era ace jump 2006–2010 vs 1996–2000 using `event_year` buckets—equipment narrative without line data.
535. Covid gap: compare March–June 2020 match volume zeros vs 2019 baseline weekly counts.
536. Rankings roll-forward: simulate Monday rank for winner using points rules omitted—explicit negative capability statement plus sensitivity toggle if points known.
537. Multi-surface fortnight: players winning titles on clay and hard within 21 days using `tourney_date` diffs—versatility burst detection.
538. Defensive bonus: wins with `w_ace` below tour median but `minutes` above tour median—grinder signature.
539. Aggressive bonus: wins with `w_ace` top decile and `minutes` bottom quartile—quick strike signature.
540. Shot-quality placebo: randomize MCP rally lengths within match bootstrap concept—stability of winner rate estimator (methodology question).
541. Opponent quality adjust MCP stats: subtract opponent’s charted baseline from each match z-score—debiased leaderboard sketch.
542. Time decay weights: exponentially weight last-2-season MCP aggregates vs full career for direction usage entropy—recency sensitivity.
543. Avoid direct ATP–WTA statistic comparisons where format differs; instead compare within-tour decile migration of `w_1stIn/w_svpt` from 1995 to 2015 separately for ATP and for WTA.
544. Lefty serve disadvantage myth: as returner losses, is `l_1stWon` lower vs lefty servers after controlling rank gap?
545. Bagel mitigation: players avoiding 6-0 sets conceded more than tour average despite many matches—defensive floor metric.
546. Ace concentration within match: Gini on simulated per-set ace counts if set boundaries parsed from `score` for ATP.
547. Double fault clustering: matches where `w_df` concentrates in single set inferred from partial stats absence—flag limits.
548. Medical timeout proxy unavailable—use retirement `match_status` rate following ultra-long prior match within 48h for same player if dates dense.
549. Travel fatigue: change in win% when previous tournament `tourney_name` continent token differs from current (heuristic intercontinental).
550. Altitude proxy table: events whose names include ‘Madrid’, ‘Mexico’, ‘Bogota’ vs sea-level name list—ace lift comparison with documented caution.
551. Court colour not stored—use surface + indoor keyword crossed with ace rate for hard subclasses.
552. Rain delay not stored—ignore; use only completed `match_status` rows for fair splits.
553. Junior slam graduates: players first appearing in slam MD with `winner_entry` qualifying strings—later peak rank correlation.
554. Ranking protection used flag if encoded—performance of protected entrants vs direct entrants same rank band.
555. Pull-out cascade: count tournaments where >3 seeds lose R1—injury wave indicator.
556. Seeding accuracy: mean absolute error between seed number and rank for top 16 seeds when both present annually.
557. Lucky loser performance: if `winner_entry`/`loser_entry` distinguishes, compare main-draw win% vs qualifiers baseline.
558. LLM question-to-table routing test: list 10 phrases that must pull `wta_mcp_shot_direction` (name as deployed) vs `wta_matches` only.
559. SQL injection regression: ensure API escapes ranking date filters—security note adjacent to analytics.
560. Caching staleness: if Redis TTL 300s, maximum drift between repeated identical aggregation during live event ingestion—edge case.
561. Batch export: chunked `event_year` extracts for DuckDB `COPY` to Parquet—maintain MCP referential joins in exported partitions.
562. Explain-plan sport: which index on `(tourney_name, event_year)` reduces scans for Section 3 questions empirically?
563. Materialized view refresh lag: staleness detection comparing latest `tourney_date` in base vs view.
564. Player id migration: detect renamed `player_id` chains via identical `full_name` and overlapping ranking weeks—entity resolution checklist.
565. Unicode normalization NFKC on names before join—effect on MCP linkage rate if applied.
566. Soundex false-positive rate on `winner_name` matching—discourage fuzzy joins except QA.
567. Flag outlier `minutes` for supposedly completed matches: e.g. `minutes` > 600 or `minutes` < 20 relative to `best_of` and `score` length.
568. Validate `w_svpt` plausibility vs minimum serves implied by parsed games and tiebreaks in `score`—row-level exception report.
569. Score grammar fuzzer: unit tests for `RET`, `W/O`, `DEF` substrings in `score`—parser coverage matrix.
570. Week-of-year heatmap of MCP row `created_at` timestamps if present—operational ingestion cadence.
571. If MCP stores a chartist or source id column, partition rally-length means by that id and compare between-group variance.
572. Report Wilson score intervals for MCP-derived rates (e.g. wide-serve win %) for players with <400 charted points.
573. Propensity model for MCP coverage: logistic with predictors rank gap, surface, `tourney_level`; report odds ratios on charted vs not.
574. Scheduling confounds: state explicitly that injury responses to surface changes are descriptive only without exogenous instruments.
575. Lead–lag exploratory check: correlate tour-wide weekly ace rate with ace rate two weeks later—no causal claim.
576. Seasonality check: amplitude of Fourier first harmonic on weekly global match counts—peak alignment with slam months.
577. When testing many surfaces on the same metric, apply Benjamini–Hochberg FDR across hypotheses.
578. Document correct `GROUP BY` keys when joining MCP overview rows that may duplicate per player-side—you must not double-count service points.
579. Compare SQL window definitions `ROWS` vs `RANGE` when computing rolling rank volatility—DuckDB vs PostgreSQL planner notes.
580. Future schema: store doubles lineups as JSON arrays of four player ids to simplify rotation analytics.
581. Build undirected rivalry edges from ≥15 H2H matches; report highest-degree nodes—hub rivals.
582. Within the same season directed win graph, compute longest path following strictly increasing `tourney_date` for each player—win-chain leaderboard.
583. Atlantic–clay bridge workload: players counting ≥8 European clay swing matches and ≥8 North American hard matches within one season—schedule stress cohort.
584. Contrast mean `winner_rank` of Istanbul/Open-era expansion events vs established 500s if name tokens identify expansion era—field strength narrative.
585. For each ATP player with ≥300 wins, compute skewness of per-match `minutes` in wins—right-tail workload asymmetry.


---

**Total questions:** 585
