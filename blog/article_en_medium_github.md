# Is the Era of "Dry Sake" Really Over?

### What 140 years of data reveal about where Japan's sake trend really stands

"Sake should be dry" — this phrase, once common in Japanese izakayas, now sounds a bit dated. The top of the rankings is dominated by sweet, fruity sake. But is the age of *karakuchi* (dry) really behind us?

Pulling together publication data from the National Diet Library of Japan, about 370,000 reviews from SAKETIME (Japan's largest sake review site), and Google Trends search data, what emerged was not a simple "from dry to sweet" story. The landscape at the top of the rankings and the words everyday consumers use to shop for sake don't necessarily line up.

---

## Starting point: a claim made in a YouTube video

It all started with a YouTube video about sake. Looking at the top-ranked brands on SAKETIME, the presenter concluded that "the top sake brands are all *ama-uma* (sweet-umami), juicy ones."

Juyondai, Aramasa, Jikon, Hanaabbi — each of these brands has depth that can't really be summed up in a single word, but the observation has intuitive appeal. Whether it's fair to call that "the trend of sake as a whole," however, is another question. And if top-ranked sake really is overwhelmingly sweet, what happened to the long-standing common sense that "dry is good sake"?

So in this piece, I traced the long-term historical flow of language first, then examined the evaluation structure of the enthusiast community, and finally compared it with the search behavior of general consumers. The aim is to avoid jumping to conclusions from a single dataset, and instead see how "dry" survives across different layers.

---

## 1. When did "dry = good sake" really take hold?

To look at the long span, I first checked the frequency of the words *karakuchi* (dry), *amakuchi* (sweet), *tanrei* (light/crisp), *hojun* (rich), *ginjo*, and *junmai* using the National Diet Library's **NDL Ngram Viewer**. One caveat: this data is not limited to sake — it reflects word frequency across all publications. So this is not strictly a "history of sake" but rather a supplementary line for seeing how the era's language was changing.

![Frequency of taste-related words in Japanese publications (1880–2000). Source: NDL Ngram Viewer.](https://raw.githubusercontent.com/s00048ri/saketimes-analysis/main/blog/medium/fig1_ndl.png)
*Figure 1: Frequency of taste-related words in Japanese publications (1880–2000). Source: NDL Ngram Viewer.*

In this long-term data, "sweet" (*amakuchi*) was by far the most used word during the Meiji era (1880s). As often pointed out in the literature, sake discourse in the Edo period was originally centered on "sweet." That tendency may be reflected here.

"Sweet" then slowly declined over the following century, while "dry" (*karakuchi*) rose sharply from the 1970s onward. Since *tanrei* (light/crisp), a term specifically tied to sake, was rising at the same time, it's natural to read this — at least at the level of discourse — as the "*tanrei karakuchi*" (light and dry) boom taking firm hold during this period.

One common argument explains "dry" worship as a reaction against *sanzoshu* (the low-grade post-war sake made by adding brewing alcohol, sugars, and acidulants to pad out rice-short brews to roughly three times the original volume — notorious for its cloyingly sweet, sticky character). But from this data, I couldn't find evidence that "dry" increased at the publication level immediately after WWII.

The lower panel shows "ginjo" exploding in frequency from the 1980s — a data-backed confirmation of the ginjo boom. Put differently, the feeling that "dry is good sake" is a relatively new value in the long history of sake. Rather than having dominated consistently since the immediate post-war years, it's closer to reality to see it as a narrative that became strongly institutionalized and mainstreamed in the 1970s–80s.

---

## 2. Top brands on the enthusiast platform are indeed sweet-leaning

Next, let's turn to all 5,386 brands and about 370,000 reviews from SAKETIME. What we can grasp here is not "the entire market" but the preferences of the review-writing enthusiast community. Even so, it's a powerful vantage point for seeing what's highly valued right now.

### Structured data: higher rank, sweeter and lighter

On SAKETIME, users register "sweet/dry" (5 levels from dry +2 to sweet +2) and "body" (5 levels from light +2 to heavy +2) along with their reviews. When aggregated by ranking tier, the profile of top brands became quite clear.

![Sweet vs Dry rate by ranking tier](https://raw.githubusercontent.com/s00048ri/saketimes-analysis/main/blog/medium/fig2_sweet_dry.png)
*Figure 2: Sweet rate and dry rate by ranking tier. Data: SAKETIME, 370K reviews.*

- **Sweet rate** (sweet +1 or above): 67.3% in Top 10, 30.2% in ranks 101–500, 27.6% in ranks 501+
- **Dry rate** (dry +1 or above): only 3.7% in Top 10, 25.7% in ranks 101–500, 29.3% in ranks 501+
- **Rich rate** (heavy +1 or above): 11.2% in Top 10, 18.4% in ranks 101–500

The gap in sweet rate between Top 10 (67%) and 501+ (28%) is a full 40 percentage points. Conversely, the dry rate in ranks 501+ (29%) is more than seven times higher than in Top 10 (4%). It's fair to say that in the top-ranking world, "sweet equals highly rated" holds.

But this is not the same thing as "rich, heavy in umami." In fact, the rich rate is *lower* in higher ranks. What concentrates at the top is sake that's sweet yet not too heavy — with clean definition and drinkable over time. The YouTube video's point about "sweet" was correct, but "umami" and "juicy" need to be handled more carefully.

### Review text highlights the strength of "fruity"

To check nuances that structured data alone can't capture, I also compared keyword frequencies in review text.

![Keyword frequency in review text by ranking tier](https://raw.githubusercontent.com/s00048ri/saketimes-analysis/main/blog/medium/fig3_text_keywords.png)
*Figure 3: Taste keyword frequency in review text by ranking tier.*

- **Sweet-type keywords**: 32.8% in Top 10, 26.8% in ranks 501+
- **Dry-type keywords**: 3.7% in Top 10, 16.8% in ranks 501+ (dramatically lower at the top)
- **Fruity-type**: 24.7% in Top 10, 13.3% in ranks 501+ (roughly double at the top)
- **Rich-type**: 17.9% in Top 10, 23.2% in ranks 501+ (actually lower at the top)

What stands out is that the higher the rank, the less "dry" is spoken of, and the more "fruity" appears. Sweet-type keywords are also slightly more common at the top, but beyond that, what characterizes the impression of top brands can be described as "elegance with a sense of fruit."

![Top 9 sake flavor profiles](https://raw.githubusercontent.com/s00048ri/saketimes-analysis/main/blog/medium/fig4_radar.png)
*Figure 4: Top 9 sake flavor profiles — keyword analysis of 370K reviews on SAKETIME.*

Looking at individual profiles of the Top 10, Hanaabbi's fruity rate of 37% and Hinotori / Miyakanbai's sweet rate of 44% stand out. On the other hand, Juyondai — ranked #1 — shows a dry rate of just 1.8%, with the sweet rate not especially high either: a balanced type with no extreme leanings. That is, the aesthetic of top brands is closer to "how to reconcile elegance and refinement" than "sweet is good."

![Taste distribution comparison by ranking tier](https://raw.githubusercontent.com/s00048ri/saketimes-analysis/main/blog/medium/fig5_heatmap.png)
*Figure 5: Taste distribution (body × sweet/dry) by ranking tier. Each cell = % of total.*

When you overlay the distribution of sweet/dry and body, top brands cluster in "normal body × sweet-leaning." What emerges is not a victory of "heavy and rich" but the advantage of sake that is "moderately light, with lifted aroma, where the sweetness shows cleanly."

---

## 3. But it can't be said that everything is going sweet

So, is the community as a whole going all-in on sweet? Looking at the 2017–2025 time series, the picture is a bit more complex.

### In structured data, sweet is settling in but not running away with it

![Time series of taste tendencies](https://raw.githubusercontent.com/s00048ri/saketimes-analysis/main/blog/medium/fig6_trend_structured.png)
*Figure 6: Taste trends over time — structured data, all brands.*

- The **sweet rate** has maintained the highest level throughout, but has gradually declined from 42% in 2017 to 37% in 2025
- The **dry rate** fell until around 2022, then recovered somewhat recently (from 18% back to the low 20s)
- The **rich rate** continues to fall from 20% to 14% — the trend away from "heavy sake" is relatively clear
- The **light rate** remains stable at 28–30%

What's important here is that the observation "sweet has become mainstream" and the conclusion "dry is over" are not the same thing. Across the community as a whole, at least, while sweet has become the new orthodoxy, dry still maintains a certain presence.

### In text analysis too, what's growing is "fruity" more than sweet

![Keyword frequency trends over time](https://raw.githubusercontent.com/s00048ri/saketimes-analysis/main/blog/medium/fig7_trend_text.png)
*Figure 7: Taste keyword trends over time — review text analysis, all brands.*

In review text too, the clearest rise is in fruity-type expressions — from 17% in 2017 to 25% in 2025. Sweet-type words have settled in as the mainstream, so their growth has slowed; dry-type words show a bottoming-out after a temporary dip.

So rather than "a full shift from dry to sweet," the more accurate description is: "sweet and fruity have become the standard language of the top, while the community as a whole is diversifying."

---

## 4. In the general consumer's search axis, "dry" is still strong

Finally, Google Trends. What this measures is not taste itself but "the words people use when they look for sake." So this is not a direct measurement of preference, but rather data on the strength of classification and search terms.

![Google Trends for sake-related search terms](https://raw.githubusercontent.com/s00048ri/saketimes-analysis/main/blog/medium/fig8_google_trends.png)
*Figure 8: Google Trends — sake-related search terms in Japan (2004–2025). 12-month moving average.*

In this data, "sake dry" consistently and significantly exceeds "sake sweet." Moreover, "dry" has been on a long-term upward trend from 2004 to 2025, while "sweet" has also grown gradually. In other words, in general consumer search behavior, "dry" remains an extremely strong entry-point word.

Of course, search volume doesn't directly equate to the strength of preference. "Dry" is a term easily understood at the shop counter and likely functions as a safe, well-recognized selection label. Still, it's hard to say that the word "dry" is already obsolete.

### Three layers

Organizing the observations so far, the landscape around sake taste has a three-layer structure.

- **Layer 1: Top of the ranking (Top 10–50)** — Sweet, fruity, and light-bodied dominate. Sweet rate 67%, dry rate 4%.
- **Layer 2: Lower ranks (501+)** — Sweet rate 28%, dry rate 29%. Sweet and dry are roughly balanced; many dry brands still exist.
- **Layer 3: General consumers (Google search)** — "Dry" remains the primary keyword consistently, and search volume is still growing.

And, as we saw in the previous section, even in SAKETIME's overall review pool, the dry rate is rising again in recent years. Even within the enthusiast community, a swing back toward dry is beginning.

---

## 5. Conclusion: Is the era of "dry sake" over?

Looking only at the top of the rankings, the answer really does look like "it looks pretty much over." Because what's highly rated now is sake that is sweet, fruity, and not too heavy.

But broaden the view and the answer changes. The long tail of the rankings still contains many dry brands (29% dry rate in 501+), "dry" remains the dominant exploration term in Google search (2.5× that of "sweet"), and even the community as a whole hasn't fully retreated from dry. What emerges is not "sweet has become the orthodoxy" but "the evaluation axis of top brands has shifted" — and that shift doesn't entirely align with the language of the broader market.

Zooming out across roughly 140 years, a large cycle of swing-back comes into view: sweet (Meiji) → dry (1970s–90s) → sweet / fruity (late 2010s onward). But what's happening now is not a simple "return to sweet." While sweet and fruity have settled in as the new orthodoxy, dry is also showing signs of resurgence — taste itself may be diversifying.

> **The era of "dry = good sake" is, at least, not over. But that word is no longer the best description of the value of top brands. Today's sake is being reorganized around sweet and fruity, yet it hasn't thrown dry away either.**

---

## Appendix 1: SAKETIME overview and caveats for reading the rankings

Looking at SAKETIME as a whole, the correlation between rating scores and review counts is very high (0.888 on a log scale). This isn't simply "better sake gets more reviews" — it likely includes visibility bias: "well-known sake gets rated higher," "buzzy sake stays at the top." Treating the top of the rankings as "a miniature of the overall market" isn't safe.

![Rating score vs review count](https://raw.githubusercontent.com/s00048ri/saketimes-analysis/main/blog/medium/appfig1_rating_reviews.png)
*Appendix Figure 1: Rating score vs. review count. Top 10 brands labeled.*

This matters when reading the central conclusions of this piece. What we're looking at here is "the taste of brands that currently attract high ratings" — not direct measurements of sales volume across the sake market or actual drinking behavior of general consumers.

---

## Appendix 2: Differences in rating by classification

By specific-name classification (*tokutei meishoshu*), junmai daiginjo (4.16) and junmai ginjo (4.05) show higher average ratings, while honjozo (3.79) and futsushu (regular, 3.75) are relatively lower. This is intuitive, but the gap is only about 0.4 points — not decisive. Classification alone doesn't determine rating.

![Average rating by classification](https://raw.githubusercontent.com/s00048ri/saketimes-analysis/main/blog/medium/appfig2_specname.png)
*Appendix Figure 2: Average rating by sake classification (tokutei meishoshu).*

---

## Appendix 3: Independent verification with Sakenowa data

To check that the main conclusions aren't driven by SAKETIME-specific biases, I cross-checked with the flavor data from Sakenowa, which offers a public API. Sakenowa is a sake community app with over one million check-in records. Its public API provides flavor charts (6-axis numerical values: floral / rich / heavy / mellow / light / dry) for about 3,100 brands, along with 141 flavor tags.

![Sakenowa flavor chart by ranking tier](https://raw.githubusercontent.com/s00048ri/saketimes-analysis/main/blog/medium/appfig3_sakenowa.png)
*Appendix Figure 3: Sakenowa flavor chart — 6-axis average by ranking tier. Source: Sakenowa Data Project (sakenowa.com).*

The results largely agreed. In the 6-axis flavor charts, the higher the rank, the higher "floral" (1–10: 0.50 → outside ranking: 0.35) and the lower "heavy" (1–10: 0.24 → outside: 0.35). Among flavor tags, the "dry" tag appears in 0% of top-10 brands but reaches 78% in ranks 51–100. "Fruity" is 100% in Top 10 and 33% outside the ranking.

Dry and heaviness come to the fore more at the middle and lower ranks, while at the top, the direction "elegant and light, with good balance" is reproduced. At least the skeletal finding — "the higher the rank, the more fruity-leaning; not heavy and dry" — is supported by another dataset.

---

## Methods and data sources

- **SAKETIME data**: Python-based scraping (BeautifulSoup). Ranking info, brand details, and about 370,000 reviews for 5,386 brands.
- **Text analysis**: Keyword-frequency aggregation, cross-analysis by ranking tier and by year.
- **Sakenowa data**: Sakenowa Data Project API — flavor charts (6 axes) and flavor tags (141) for about 3,100 brands. Data from Sakenowa (https://sakenowa.com), processed and adapted for this analysis.
- **Publication data**: National Diet Library NDL Ngram Viewer API (OCR text of about 2.3 million books and magazines).
- **Search trends**: Google Trends (via pytrends, region: Japan, 2004–2025).

**[On NDL Ngram Viewer]** NDL Ngram Viewer data reflects word frequencies across all publications, not limited to sake contexts. For example, "dry" (*karakuchi*) also includes things like "dry commentary" in criticism, and "sweet" (*amakuchi*) can include references to mild curry. Terms specifically associated with sake such as *tanrei*, *ginjo*, and *junmai* are relatively sake-contextual, but other usages are strictly possible. This should be treated as a supporting reference for long-term trends, not a precise measurement of sake discourse.

**[On Sakenowa flavor tags]** Sakenowa's flavor tags have a different nature from SAKETIME's taste ratings (which are exclusive choices between sweet and dry). They're an accumulation of characteristic words extracted from review text, with an average of 9.4 tags per brand. 30% of brands have both "sweet" and "dry" tags. Tag frequency indicates how often a taste is mentioned, not an exclusive classification.

**[On reviewer bias]** SAKETIME's 370,000 reviews were posted by 4,625 users, but the distribution is heavily skewed. The top poster alone contributed about 14,000 reviews (3.8% of the total). The top 100 users (2.2%) account for 37% of all reviews; the top 500 (10.8%) account for 72%. Results may therefore be strongly shaped by the preferences of a relatively small group of heavy reviewers.

---

*Data retrieved: April 14, 2026*
