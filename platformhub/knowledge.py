from datetime import date


ARTICLES = [
    {
        "slug": "button-copy-should-describe-the-consequence",
        "title": "Button copy should describe the consequence",
        "date": date(2026, 8, 24),
        "dek": "A button is a promise about what happens next. Many interfaces waste that promise on vague words.",
        "body": [
            """I pay close attention to buttons because they reveal whether a product team has thought through the user’s next moment. “Submit” is technically correct in thousands of interfaces. It is also usually lazy. A person is rarely trying to submit something. They are trying to book a call, send a brief, save a draft, pay an invoice, or create an account. The button should name that consequence.""",
            """This sounds like a small copy decision until you watch someone hesitate. The hesitation often starts when the interface asks for one action while the person is thinking about another. A form may ask for personal details and end with “Continue.” Continue to what? If the next screen charges money, the ambiguity matters. If the next screen only reviews the information, that matters too. Good interface language reduces the gap between what the system knows and what the person knows.""",
            """I dislike buttons that try to become miniature advertisements. “Unlock your potential” is poor button copy when the actual action creates an account. The phrase makes the interface less clear at the exact point where clarity matters most. Persuasion should already have happened in the page. The button has a narrower job: tell me what my click will do.""",
            """There is also a trust issue. Product copy becomes suspicious when every control is dressed up as a benefit. People notice when a site avoids plain verbs around payment, cancellation, data sharing, or commitment. A good product can afford precise language. “Start 14-day trial” is stronger than “Get started” because it carries useful information. “Delete project” is better than “Confirm” because it names the irreversible act.""",
            """The best button copy usually comes from asking a simple question: what new state will exist after this click? If the answer is “the message will be sent,” use “Send message.” If the answer is “we will create an invoice and take the user to payment,” say that before the click and label the action accordingly. This is interface logic expressed in language.""",
            """When we work on product language, buttons are rarely the first thing a client mentions. They often become some of the most important edits. A product feels more considered when small decisions carry the same precision as the headline. Users may never praise the wording. They simply move through the product without having to stop and interpret it."""
        ],
    },
    {
        "slug": "mobile-copy-is-partly-a-layout-decision",
        "title": "Mobile copy is partly a layout decision",
        "date": date(2026, 7, 13),
        "dek": "A sentence can be clear on a laptop and clumsy on a phone. The words and the layout have to be judged together.",
        "body": [
            """Desktop screens make average copy look better than it is. There is room for long headings, explanatory text, side notes, and generous spacing. Move the same page onto a narrow phone and every weakness becomes physical. The heading wraps into five lines. The call to action falls below the fold. A label pushes the value out of view. Suddenly the copy problem is also a geometry problem.""",
            """Treating mobile as a smaller version of desktop misses what changes when space disappears. Some ideas need fewer words on a phone because the screen has less space. Other ideas need more direct explanation because the surrounding visual context has disappeared. Responsive writing is about deciding what information must survive when the layout changes.""",
            """Navigation is a good example. A desktop header can carry five or six clear destinations. On mobile, those destinations may hide behind a menu. If the page itself assumes the navigation is always visible, the user can lose orientation. Small labels such as “Account,” “Back to projects,” or a clear page title become more important. The same copy can have a different job when the screen changes.""",
            """I also look at line breaks. A headline may have been written for a dramatic two-line desktop composition, then become an awkward stack of isolated words on mobile. CSS cannot solve that alone. Sometimes the sentence needs to change. A shorter verb can restore the rhythm. A noun can move earlier so the first two lines carry meaning even before the rest is seen.""",
            """Form copy needs similar care. Long helper text under every input creates a wall on mobile. I prefer putting guidance where the user needs it, then removing anything that merely repeats the label. Error messages should say what happened and how to fix it without forcing the person to scroll back through a paragraph.""",
            """I think teams should review copy at the narrowest useful width before they approve it. This changes the conversation. People stop asking whether a sentence sounds good in a document and start asking whether it works inside the product. That is where interface writing becomes real. Words occupy space. They compete with controls. They shape pace. A mobile screen makes those facts impossible to ignore."""
        ],
    },
    {
        "slug": "you-can-hear-when-a-company-misunderstands-its-customer",
        "title": "You can hear when a company misunderstands its customer",
        "date": date(2026, 6, 28),
        "dek": "Weak customer knowledge shows up in vocabulary long before it shows up in strategy decks.",
        "body": [
            """A company can have a detailed customer profile and still sound as if it has never spoken to a customer. I see this when the website uses the company’s internal categories instead of the words people use to describe their own problem. The copy may be polished, yet the reader has to translate every paragraph into something familiar.""",
            """The easiest example is service naming. A business might describe “integrated knowledge production solutions.” A customer may be trying to turn twenty interviews into a report by Friday. Those are connected ideas, but only one begins where the customer is standing. If you understand the person well, you know which language belongs on the first screen and which language can wait.""",
            """Demographics give only part of the customer picture. Age, location, job title, and industry can still be useful. I care more about the words people use when they are frustrated, uncertain, comparing options, or explaining the task to a colleague. Those sentences contain the real buying context. They tell you what feels urgent, what needs proof, and what the person is afraid of getting wrong.""",
            """This matters in AI products because teams often describe the model instead of the work. Most users care less about retrieval, orchestration, or a particular model family than they care about the result. They want the system to read their documents, keep citations attached to claims, and return something they can use. Technical detail belongs where it helps them evaluate that result.""",
            """I also distrust audience copy that tries to sound familiar through slang. Knowing a customer means understanding their level of knowledge and respecting their time. A lawyer and a product manager can both prefer simple English. Simple English can still respect the professional language each audience needs.""",
            """When we research customers, I want examples of actual questions, objections, emails, support messages, and sales calls. Then the writing becomes easier. We stop inventing a voice and start noticing one. The strongest copy often feels obvious after this work because it uses the words the customer already needed. That obviousness is earned."""
        ],
    },
    {
        "slug": "persuasive-writing-gets-weaker-when-it-tries-too-hard",
        "title": "Persuasive writing gets weaker when it tries too hard",
        "date": date(2026, 5, 9),
        "dek": "Pressure, exaggeration and constant benefit language can make a strong offer feel less credible.",
        "body": [
            """I am suspicious of copy that wants every sentence to sell. You can feel the pressure in phrases such as “transform your workflow,” “unlock unmatched value,” or “revolutionize the way you work.” Even when these claims are true, they ask the reader to accept a conclusion before the page has shown enough evidence.""",
            """Persuasion works better when the writing understands sequence. First establish the situation accurately. Then show what changes. Give the reader enough detail to judge whether the change matters to them. A strong offer becomes persuasive through relevance and proof. Constant emotional volume weakens that effect.""",
            """Specific language helps. “We review the sources, draft the report, and return an editable document” gives me something I can evaluate. “We empower teams with high-impact content” does not. The first sentence also creates useful questions: how many sources, what kind of report, how long, what happens after review? Good persuasive copy invites the right questions because the offer can survive them.""",
            """I think one of the worst habits in modern landing pages is treating doubt as an enemy. Real buyers have doubts for good reasons. They want to know what they are paying for, whether they will lose control, how revisions work, and whether the service fits their situation. Copy that answers those concerns directly often converts better because it respects the decision.""",
            """The same principle applies to urgency. If a deadline is real, explain it. If capacity is limited, say why. Artificial countdowns and invented scarcity train people to distrust the page. Persuasion should reduce uncertainty around a good decision. Tricks usually increase uncertainty.""",
            """This is especially important for expensive services. A serious client is rarely persuaded by a bigger adjective. They are persuaded when the provider seems to understand the work, the risks, and the expected result. That is why I prefer copy that sounds like someone who has done the job before. It can be confident without performing confidence. The details carry the weight."""
        ],
    },
    {
        "slug": "ai-writing-has-a-rhythm-problem",
        "title": "AI writing has a rhythm problem",
        "date": date(2026, 4, 22),
        "dek": "The most obvious machine-like writing is often exposed by sentence behaviour rather than vocabulary.",
        "body": [
            """People often try to detect AI writing by looking for certain words. That catches some bad output, but the deeper problem is rhythm. Many generated passages move with the same predictable logic: announce a point, restate it more dramatically, add a contrast, then close the paragraph with a sentence that tells you how important the point was. The words change. The behaviour stays.""",
            """This is why replacing “delve” or “landscape” does very little. A paragraph can avoid every cliché and still feel generated because each sentence has the same job. Human writing is usually less tidy. We spend more time on one idea when it matters. We move quickly through what the reader already understands. We sometimes let a concrete example do the explanatory work.""",
            """I notice generated rhythm most in conclusions. The sentence has already made the point, then another sentence arrives to summarize it with attitude. That extra line often sounds polished in isolation. In context it weakens the writing because it delays the reader without adding meaning. Cutting it is one of the fastest ways to improve AI-assisted copy.""",
            """There is also a strange dependence on balanced structures. Models like symmetrical sentences because symmetry is statistically comfortable. Too much symmetry makes prose feel staged. Real arguments have uneven weight. One side of a comparison may need three sentences while the other needs six words. Forcing them into matching shapes changes the thought.""",
            """Our approach to humanizing text starts with function. What does each sentence contribute? If two sentences do the same work, one should probably go. If a transition only announces what the next paragraph already makes clear, remove it. If a sentence exists because the model wanted a satisfying cadence, ask whether the reader needed it.""",
            """Good writing can openly use AI. What matters is whether someone has judged the result. Someone has decided what matters, what can be cut, where the tone should tighten, and where detail is worth the space. AI can produce material quickly. Editorial judgment gives the material a shape worth keeping."""
        ],
    },
    {
        "slug": "good-ux-writing-earns-the-right-to-disappear",
        "title": "Good UX writing earns the right to disappear",
        "date": date(2026, 3, 6),
        "dek": "The best interface copy is often remembered only when it fails.",
        "body": [
            """UX writing has an unusual success condition: people often notice it only when it fails. They notice the product. They finish the task. The words quietly explain the next action, the current state, and any consequence that deserves attention. That invisibility is earned through careful choices.""",
            """Interface language can still have personality, and that personality can help a product feel coherent. The problem begins when personality competes with the task. An error message is a bad place for a joke if the user has just lost work. A payment failure needs the reason, what happened to the money, and what the person can do next.""",
            """The same is true for empty states. Many products fill them with cheerful filler because the blank screen feels uncomfortable. I would rather use that space to answer the user’s next question. Why is this empty? What creates the first item? Is there an example worth showing? A good empty state turns absence into instruction.""",
            """I also think UX writing should expose state changes clearly. Saving, sending, publishing, deleting, and paying are different actions because they create different consequences. Interfaces become stressful when the language blurs those differences. “Done” is often too vague. “Invoice sent” tells the user what the system did and gives them a stable point to move from.""",
            """There is a relationship between good UX copy and good engineering. The writer needs to know what the system can actually guarantee. If a file is still processing, the interface should not say it is ready. If a payment is pending verification, the success screen should not claim the transaction is complete. Precise copy depends on precise product states.""",
            """This is why I prefer UX writing to happen inside the product work rather than at the end. The writer should see the flow, the errors, the mobile version, and the loading states. Once you see the interface behaving, many copy decisions stop being stylistic. They become part of the product logic."""
        ],
    },
    {
        "slug": "research-changes-the-sentence-while-you-are-writing-it",
        "title": "Research changes the sentence while you are writing it",
        "date": date(2026, 2, 18),
        "dek": "Research changes what a writer is willing to claim.",
        "body": [
            """I dislike production processes that separate research and writing too neatly. The researcher delivers notes, then the writer turns them into prose. That can work for simple work, but serious writing usually requires movement in both directions. A sentence creates a question. The question sends you back to a source. The source changes the sentence.""",
            """This happens most often around confident claims. A briefing may say a market is “growing rapidly.” Once you start writing, that phrase demands a number, a period, and a comparison. You discover that one source measures revenue while another measures users. The original claim becomes narrower. That narrowing is progress.""",
            """Writing is useful because it exposes where the research remains unsettled. A bullet point can hide uncertainty. A paragraph cannot hide it as easily because the relationships between ideas have to be stated. Who caused what? Compared with when? Under which conditions? When the sentence becomes awkward, the underlying evidence is often awkward too.""",
            """The reverse is also true. Research changes structure. You may begin with a simple argument and find that the evidence supports a different order. One section becomes less important. A caveat moves earlier because it affects everything that follows. Good production work allows the document to change shape as understanding improves.""",
            """This matters for AI-assisted research because models are very good at giving an answer shape before the evidence deserves that shape. A fluent summary can make weak support feel settled. We try to resist that. Claims should become more precise as the source work improves. If the evidence remains mixed, the language should show that honestly.""",
            """For us, research and writing are one conversation. The document is a test of the evidence. The evidence is a test of the document. Keeping them close produces work that feels less assembled because the thinking developed inside the writing."""
        ],
    },
    {
        "slug": "brand-voice-matters-most-in-boring-places",
        "title": "Brand voice matters most in boring places",
        "date": date(2026, 1, 12),
        "dek": "A brand voice that only appears in campaigns is decoration. Product and service language prove whether the voice is real.",
        "body": [
            """I learn more about a brand from its password reset email than from most campaign headlines. The reset email is boring, necessary, and easy to neglect. That is exactly why it is revealing. If the company’s voice disappears the moment the work becomes operational, the voice was probably a marketing costume.""",
            """Brand language should survive invoices, error messages, receipts, cancellation screens, account settings, and support replies. These are the moments when people are trying to do something specific. The writing has to be useful first, but usefulness still leaves room for character. A calm company can sound calm. A direct company can be direct. A precise company should be especially precise when money or access is involved.""",
            """I am cautious about brand voice guides full of adjectives. “Bold, warm, human, confident” can describe almost any company. Examples are more valuable. How do we say no? How do we explain a delay? What do we call a customer when they have not paid yet? Do we use contractions in legal notices? What happens to the voice when someone is angry? Those choices make the voice operational.""",
            """The boring places also reveal whether a company respects the reader. A cancellation page that hides the exit behind persuasive copy says something about the brand. A refund email that avoids naming the amount says something too. Tone is partly ethics. Language controls how clearly a person can understand what is happening to them.""",
            """I think teams should test their brand voice on the least glamorous page in the product. Rewrite the failed-payment email. Rewrite the data-export screen. Rewrite the message shown when a subscription ends. If the voice still feels useful and recognisable there, it probably has substance.""",
            """Campaign copy gets attention, but operational copy builds memory through repetition. Customers see it when they are doing real work with you. That is where a brand becomes a habit rather than an impression."""
        ],
    },
    {
        "slug": "desktop-copy-often-fails-on-mobile",
        "title": "Desktop copy often fails on mobile",
        "date": date(2025, 12, 19),
        "dek": "Responsive design can rearrange a page perfectly and still leave the writing in the wrong order.",
        "body": [
            """A responsive layout can pass every technical check and still communicate badly on a phone. The problem is often reading order. Desktop designs place context in a left column and detail on the right. On mobile those blocks stack. If the copy was written assuming they would be seen together, the stacked version can become confusing.""",
            """Cards create the same problem. A row of three desktop cards feels like a comparison because the eye can scan across them. On mobile, each card becomes a separate screenful. Repeated introductions that felt harmless on desktop become exhausting. Pricing details may appear hundreds of pixels after the service name. The user has to remember more because the interface can show less.""",
            """Mobile review should include content order alongside spacing. Ask what the person sees before the first scroll. Ask whether a heading still makes sense after the supporting visual has moved below it. Ask whether the call to action arrives before enough information has been given. The phone exposes sequence problems quickly.""",
            """I also look for accidental drama. Very large desktop typography can become absurd on a small screen. A six-word headline may fill the entire viewport. That can be beautiful when the sentence deserves the space. It can also trap the user behind branding when they came to find a price, a setting, or a form. Scale should serve the task.""",
            """Mobile copy benefits from stronger nouns and verbs because space is expensive. Longer sentences can still work. The real task is removing setup that relies on visual room. A precise sentence can be long and still work well on a phone if the information arrives in the right order.""",
            """For many people, the phone is the site. I think copy should be approved there with the same seriousness as the desktop composition. If the words only work at 1440 pixels, the writing is unfinished."""
        ],
    },
    {
        "slug": "clarity-can-become-generic",
        "title": "Clarity can become generic if every brand sounds the same",
        "date": date(2025, 11, 7),
        "dek": "Clear writing is essential, and a company still needs a voice people can recognise.",
        "body": [
            """The internet has improved at clear copy and become more repetitive at the same time. Product pages are shorter. Headings are simpler. Buttons are easier to understand. Those are good changes. Yet many companies now sound almost interchangeable because they use the same vocabulary for value, speed, simplicity, and growth.""",
            """Clarity became a style when it should have remained a property. You can be clear in many voices. A sentence can be technical and clear. It can be dry and clear. It can be playful and clear. The problem starts when teams confuse clarity with one approved startup dialect: short headline, soft promise, familiar benefit phrase, friendly call to action.""",
            """AI accelerates this convergence because models are trained on the language everyone has already used. Ask for clean SaaS copy and you often get the average of thousands of existing SaaS pages. The result may be readable. It rarely gives the reader a reason to remember who said it.""",
            """The way out is usually more knowledge. Specific language comes from knowing the product well enough to name what it actually does, knowing the customer well enough to describe the real situation, and knowing the company well enough to choose what it is willing to sound like. Voice is hard to generate from adjectives because adjectives do not contain experience.""",
            """I prefer a sentence that could only belong to one company. A recognisable sentence can be plain. It may contain a detail competitors would avoid, a limitation stated plainly, or a point of view about how the work should be done. Distinction often comes from being willing to say something narrower than the market category.""",
            """Clear copy should reduce effort for the reader. Distinctive copy should increase recognition. The two goals can live together. The strongest writing makes the idea easy to understand and difficult to mistake for somebody else’s."""
        ],
    },
]


ARTICLE_BY_SLUG = {article["slug"]: article for article in ARTICLES}
