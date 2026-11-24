// Content of the decks built by build_decks.js. Edit text here, then: node slides/build_decks.js
const LEAN = { main: "2EC4B6", dark: "128C80", light: "E8F8F6" };   // session 3 accent
const AGILE = { main: "7BC950", dark: "3F8F22", light: "EEF8E9" };  // session 5 accent

module.exports = [
  {
    file: "Session3_Lean_Startup_Scientific_Method.pptx",
    title: "Lean Startup: the scientific method for business",
    footer: "Session 3 · Lean Startup",
    accent: LEAN,
    slides: [
      { type: "cover", label: "Session 3", title: "Lean Startup",
        subtitle: "The scientific method applied to business: from hypotheses to product–market fit and go-to-market",
        notes: "Lean Startup seen as the scientific method adapted to building a business, and how it leads to product–market fit and a tested go-to-market strategy." },
      { type: "agenda", kicker: "Session 3 · Roadmap", title: "Today's journey", items: [
        { num: "01", title: "Why science?", text: "A startup is an experiment under uncertainty." },
        { num: "02", title: "Hypotheses & experiments", text: "Falsifiable assumptions and MVPs." },
        { num: "03", title: "Innovation accounting", text: "Actionable metrics and the decision." },
        { num: "04", title: "Product–market fit", text: "Where the search ends." },
        { num: "05", title: "Go-to-market", text: "Segment, message, channel and price as hypotheses." } ] },

      { type: "section", num: "01", title: "Why science?", sub: "A startup is an experiment under extreme uncertainty." },
      { type: "rows", kicker: "01 · A startup is an experiment", title: "Uncertainty needs a method",
        items: [
          { title: "Extreme uncertainty", text: "Eric Ries: a startup creates something new when customer, problem and model are unknown." },
          { title: "Plans assume knowledge", text: "A business plan executes what you know. In a startup, most of it is guesswork." },
          { title: "Science finds answers", text: "Hypothesis, experiment, evidence, decision: the method humanity already uses for the unknown." } ],
        callout: "Lean Startup = the scientific method, adapted to building a business.",
        notes: "Ries defines a startup as an organisation creating a new product or service under extreme uncertainty. When nobody knows the answer you need a method for finding it." },
      { type: "table", kicker: "01 · The method", title: "From the scientific method to Lean Startup",
        headers: ["", "Scientific method", "Lean Startup"],
        rows: [
          ["Observe", "Study the phenomenon", "Customer discovery: get out of the building"],
          ["Hypothesis", "A falsifiable prediction", "Leap-of-faith assumptions: value and growth"],
          ["Experiment", "A controlled test", "A minimum viable product (MVP)"],
          ["Analyse", "Compare results with the prediction", "Innovation accounting: actionable metrics"],
          ["Conclude", "Accept or reject the hypothesis", "Persevere, pivot or stop"] ] },

      { type: "section", num: "02", title: "Hypotheses & experiments", sub: "Write assumptions that can fail, then test them as cheaply as possible." },
      { type: "cards", kicker: "02 · Leap of faith", title: "Two assumptions every business plan rests on",
        cards: [
          { num: "V", title: "Value hypothesis", text: "Does the product really deliver value to customers once they use it?" },
          { num: "G", title: "Growth hypothesis", text: "How will new customers discover the product, and keep coming?" } ],
        callout: "Test the riskiest one first, and write it so that it can be proven wrong." },
      { type: "template", kicker: "02 · Falsifiable hypotheses", title: "Write hypotheses that can fail",
        cards: [ { head: "Hypothesis template", rows: [
          { lead: "We believe that", fill: "a specific customer segment" },
          { lead: "Will", fill: "do something observable (not an opinion)" },
          { lead: "Measured by", fill: "one metric" },
          { lead: "We are right if", fill: "a threshold, by a date — decided before testing" } ] } ],
        exampleLabel: "Example (illustrative)",
        example: "We believe that wind-farm maintenance managers will pay 20 € per turbine per month for failure alerts. We are right if 3 of 10 pilot farms sign a contract after a three-month trial." },
      { type: "cycle", kicker: "02 · The experiment loop", title: "Build – Measure – Learn, planned in reverse",
        center: "Plan backwards: learn → measure → build",
        nodes: [
          { title: "Learn", text: "First decide what you need to learn: which hypothesis are you testing?" },
          { title: "Measure", text: "Then decide which metric would prove it right or wrong." },
          { title: "Build", text: "Only then build the smallest MVP that produces that metric. Anything more is waste." } ] },
      { type: "steps", kicker: "02 · MVP experiments", title: "An MVP is an experiment, not a small product",
        steps: [
          { title: "Smoke test", text: "Landing page for a product that doesn't exist yet. Measures sign-ups." },
          { title: "Concierge", text: "Deliver the service by hand to a few customers. Measures value." },
          { title: "Wizard of Oz", text: "Looks automated; humans behind the curtain. Measures usage." },
          { title: "Pre-order", text: "Ask for payment before building. Measures willingness to pay." },
          { title: "A/B test", text: "Two versions, split traffic. The controlled experiment." } ] },

      { type: "section", num: "03", title: "Innovation accounting", sub: "Measure like a scientist, then decide." },
      { type: "table", kicker: "03 · Metrics", title: "Actionable metrics, not vanity metrics",
        headers: ["Vanity metric", "Actionable metric"],
        rows: [
          ["Total sign-ups since launch", "Weekly active users, by cohort"],
          ["Page views", "Conversion rate of each experiment"],
          ["App downloads", "Users still active after four weeks"],
          ["“Customers love it”", "Customers who paid, renewed or referred someone"] ],
        callout: "Ries's three A's: actionable (cause and effect), accessible (everyone understands), auditable (can be checked)." },
      { type: "cards", kicker: "03 · Conclude", title: "Every experiment ends with a decision",
        cards: [
          { title: "Persevere", text: "The evidence supports the hypothesis: keep going and test the next riskiest one." },
          { title: "Pivot", text: "Part of the model is wrong: change one element (segment, need, channel, revenue model) and keep what you learned." },
          { title: "Stop", text: "The core hypothesis is rejected: stop, and spend the time on a better idea." } ],
        callout: "A rejected hypothesis is not a failure of the method. It is the method working." },

      { type: "section", num: "04", title: "Product–market fit", sub: "The destination of the search. Lean Startup is how you get there." },
      { type: "quote", text: "Being in a good market with a product that can satisfy that market.",
        by: "Marc Andreessen, 2007 — on product–market fit" },
      { type: "cards", kicker: "04 · Signals", title: "Three signals of product–market fit",
        cards: [
          { num: "40%", title: "The Sean Ellis test", text: "At least 40% of users would be “very disappointed” if they could no longer use the product." },
          { num: "→", title: "Retention flattens", text: "Each cohort's usage curve stops falling and stays flat: people keep coming back." },
          { num: "↑", title: "Market pull", text: "Word of mouth, shorter sales cycles, demand you can't keep up with." } ] },
      { type: "steps", kicker: "04 · Customer development", title: "Search first, then execute (Steve Blank)",
        steps: [
          { tag: "Search", title: "Customer discovery", text: "Is there a problem worth solving, and for whom?" },
          { tag: "Search", title: "Customer validation", text: "Will they use it and pay? Is the sale repeatable?" },
          { tag: "Execute", title: "Customer creation", text: "Create demand and scale the go-to-market." },
          { tag: "Execute", title: "Company building", text: "From a search team to a company that executes." } ],
        callout: "Product–market fit is the line between searching and executing. Scaling before it burns money." },

      { type: "section", num: "05", title: "Go-to-market", sub: "Segment, message, channel and price are hypotheses too." },
      { type: "table", kicker: "05 · Go-to-market", title: "Test your go-to-market before you scale it",
        headers: ["Decision", "Hypothesis", "Cheap test"], colW: [1.9, 3.4, 3.7],
        rows: [
          ["Beachhead segment", "This segment needs it most, and buys first", "Interviews and one landing page per segment"],
          ["Message", "This value proposition makes them act", "A/B test two messages in ads or e-mails"],
          ["Channel", "We can reach them here at an acceptable cost", "Small budget per channel; cost per customer"],
          ["Price", "They will pay this much", "Pre-orders or two price levels"],
          ["Sales motion", "Pilots turn into contracts", "Paid pilots with clear success criteria"] ] },
      { type: "cards", kicker: "05 · Growth", title: "Choose one engine of growth",
        cards: [
          { title: "Sticky", text: "Customers stay. Grow when new customers arrive faster than others leave." },
          { title: "Viral", text: "Customers bring customers. Grow when each one brings more than one new user." },
          { title: "Paid", text: "You buy customers. Grow when lifetime value exceeds acquisition cost." } ],
        callout: "Pick one engine, find the metric that drives it, and run experiments to improve that metric." },
      { type: "images", kicker: "Case · SMARTIVE", title: "SMARTIVE: the method applied",
        images: [ { path: "assets/smartive_traffic_grid.jpg", alt: "Prototype: traffic-light grid of wind turbines" },
                  { path: "assets/smartive_dashboard.jpg", alt: "Prototype: web dashboard with alarms" } ],
        points: [
          { tag: "Hypothesis", title: "Operators need a diagnostic platform", text: "Turbines stop 5–40% of the time; their data is lost." },
          { tag: "Experiment", title: "Traffic-light grid, then a dashboard", text: "Each prototype answered one question from operators." },
          { tag: "Evidence", title: "They want the diagnosis, not the platform", text: "The value was in the analysis, not in running software." },
          { tag: "Decision", title: "Pivot to SmartCast services", text: "Same data, sold as a service per turbine per month: new go-to-market." } ] },
      { type: "closing", title: "Hypothesis, experiment, evidence, decision",
        text: "Use Lean Startup to search for product–market fit, and treat your go-to-market as hypotheses to test before you scale." }
    ]
  },
  {
    file: "Session5_Agile_Project_Management.pptx",
    title: "Agile Project Management",
    footer: "Session 5 · Agile Project Management",
    accent: AGILE,
    slides: [
      { type: "cover", label: "Session 5", title: "Agile Project Management",
        subtitle: "The software development life cycle, Scrum, Kanban, Trello and Jira" },
      { type: "agenda", kicker: "Session 5 · Roadmap", title: "Today's journey", items: [
        { num: "01", title: "The SDLC", text: "Seven phases every product goes through." },
        { num: "02", title: "Agile", text: "Waterfall vs agile, and the Manifesto." },
        { num: "03", title: "Scrum", text: "Accountabilities, events, artifacts." },
        { num: "04", title: "Kanban", text: "Visual flow and WIP limits." },
        { num: "05", title: "Tools", text: "Trello and Jira in practice." } ] },

      { type: "section", num: "01", title: "The software development life cycle", sub: "The phases are always there. The question is how you go through them." },
      { type: "steps", kicker: "01 · SDLC", title: "Seven phases of the SDLC",
        steps: [
          { title: "Planning", text: "Goals, scope, budget, risks." },
          { title: "Requirements", text: "What users and the business need." },
          { title: "Design", text: "Architecture, data, interfaces." },
          { title: "Implementation", text: "Write and review the code." },
          { title: "Testing", text: "Verify it works and meets the need." },
          { title: "Deployment", text: "Release it to users." },
          { title: "Maintenance", text: "Fix, improve, operate." } ] },
      { type: "table", kicker: "01 · Two ways through the cycle", title: "Waterfall vs Agile",
        headers: ["", "Waterfall", "Agile"],
        rows: [
          ["Phases", "Sequential, once", "Repeated in every iteration"],
          ["Requirements", "Fixed up front", "Evolve with feedback"],
          ["Delivery", "One big release at the end", "A working increment every 1–4 weeks"],
          ["Change", "Expensive, avoided", "Expected and welcomed"],
          ["Risk", "Discovered late", "Discovered early, when it is cheap"] ],
        callout: "Waterfall fits known problems (a bridge). Agile fits uncertainty (a startup)." },

      { type: "section", num: "02", title: "Agile", sub: "Short cycles, working results, continuous feedback." },
      { type: "rows", kicker: "02 · Agile Manifesto (2001)", title: "Four values of the Agile Manifesto",
        items: [
          { title: "Individuals and interactions", text: "over processes and tools" },
          { title: "Working software", text: "over comprehensive documentation" },
          { title: "Customer collaboration", text: "over contract negotiation" },
          { title: "Responding to change", text: "over following a plan" } ],
        callout: "The items on the right still matter. The items on the left matter more." },

      { type: "section", num: "03", title: "Scrum", sub: "A lightweight framework built on transparency, inspection and adaptation." },
      { type: "cards", kicker: "03 · Scrum in one picture", title: "3 accountabilities, 5 events, 3 artifacts",
        cards: [
          { num: "3", title: "Accountabilities", text: "Product owner, scrum master, developers." },
          { num: "5", title: "Events", text: "Sprint, sprint planning, daily scrum, sprint review, sprint retrospective." },
          { num: "3", title: "Artifacts", text: "Product backlog, sprint backlog, increment." } ],
        callout: "Three pillars: transparency, inspection, adaptation — the same learning loop as Lean Startup." },
      { type: "cycle", kicker: "03 · Scrum events", title: "The sprint: one goal, one to four weeks",
        center: "Sprint: 1–4 weeks, one Sprint Goal",
        nodes: [
          { title: "Planning", text: "Why this sprint matters, what we can finish, and how." },
          { title: "Daily scrum", text: "15 minutes: progress towards the goal, and what blocks us." },
          { title: "Review", text: "Show the increment to stakeholders; update the backlog." },
          { title: "Retro", text: "Improve how we work in the next sprint." } ] },
      { type: "cards", kicker: "03 · Scrum team", title: "One team, three accountabilities",
        cards: [
          { num: "PO", title: "Product owner", text: "Maximises the value of the product; owns and orders the backlog." },
          { num: "SM", title: "Scrum master", text: "Makes Scrum work: coaches the team and removes impediments." },
          { num: "Dev", title: "Developers", text: "Create a usable increment every sprint. Everyone who builds, not only coders." } ],
        callout: "Cross-functional and self-managing: the team decides who does what, when and how." },
      { type: "table", kicker: "03 · Artifacts (Scrum Guide 2020)", title: "Each artifact has a commitment",
        headers: ["Artifact", "Commitment", "It answers…"], colW: [2.2, 2.4, 4.4],
        rows: [
          ["Product backlog", "Product goal", "Where is the product going, and what is next?"],
          ["Sprint backlog", "Sprint goal", "What will we achieve in this sprint?"],
          ["Increment", "Definition of done", "Is it really finished and usable?"] ] },
      { type: "template", kicker: "03 · User stories", title: "Write backlog items as user stories",
        cards: [ { head: "User story", rows: [
          { lead: "As a", fill: "wind-farm manager," },
          { lead: "I want", fill: "an alert when a turbine is likely to fail," },
          { lead: "So that", fill: "I can plan maintenance before it stops." } ] } ],
        exampleLabel: "Acceptance criteria and INVEST",
        example: "Done when the alert arrives by e-mail with turbine ID, risk level and suggested action. Good stories are Independent, Negotiable, Valuable, Estimable, Small and Testable." },
      { type: "steps", kicker: "03 · SDLC inside Scrum", title: "Every sprint is a small SDLC",
        steps: [
          { tag: "Sprint planning", title: "Plan", text: "Sprint goal and selected stories." },
          { tag: "Daily work", title: "Design & build", text: "Small slices, reviewed as you go." },
          { tag: "Definition of done", title: "Test", text: "Tested before it counts as done." },
          { tag: "Increment", title: "Deploy", text: "A usable version, ideally released." },
          { tag: "Review & retro", title: "Learn", text: "Feedback feeds the next sprint." } ] },
      { type: "stats", kicker: "03 · Two-pizza teams", title: "Why small teams win",
        stats: [
          { value: "15", label: "communication links in a team of 6" },
          { value: "66", label: "links in a team of 12" },
          { value: "1,225", label: "links in a company of 50", highlight: true } ],
        callout: "Links = n(n−1)/2. A team should be small enough to be fed with two pizzas." },

      { type: "section", num: "04", title: "Kanban", sub: "Make work visible, limit work in progress, improve the flow." },
      { type: "board", kicker: "04 · Kanban board", title: "Stop starting, start finishing",
        columns: [
          { name: "Backlog", cards: ["Pricing experiment", "Interview 5 maintenance managers"] },
          { name: "To do", cards: ["Landing page for operators"] },
          { name: "Doing", wip: 2, highlight: true, cards: ["Failure alert prototype", "Test card for alert value"] },
          { name: "Done", cards: ["Problem interviews", "Value Proposition Canvas"] } ],
        callout: "WIP limit: a new card enters Doing only when another one leaves it." },
      { type: "table", kicker: "04 · Scrum or Kanban?", title: "Two ways to use the board",
        headers: ["", "Scrum", "Kanban"],
        rows: [
          ["Cadence", "Fixed sprints of 1–4 weeks", "Continuous flow"],
          ["Roles", "Product owner, scrum master, developers", "No roles required"],
          ["Changes", "Between sprints", "At any time"],
          ["Key metric", "Velocity per sprint", "Lead time and work in progress"],
          ["Best for", "Building a product towards goals", "Support, operations, flow of requests"] ] },

      { type: "section", num: "05", title: "Tools: Trello and Jira", sub: "The tool makes the method visible. It is not the method." },
      { type: "cards", kicker: "05 · Trello", title: "Trello: simple, visual boards",
        cards: [
          { title: "Boards, lists, cards", text: "A board per project, a list per column, a card per task, with checklists, dates and members." },
          { title: "Power-Ups & automation", text: "Calendars, integrations and rules that move or update cards for you." },
          { title: "Free for small teams", text: "Up to 10 collaborators per workspace on the free plan." } ],
        callout: "Best for: student projects, small teams and simple Kanban boards." },
      { type: "cards", kicker: "05 · Jira", title: "Jira: Scrum and Kanban at scale",
        cards: [
          { title: "Backlog & sprints", text: "Epics, stories, sub-tasks; story points; plan sprints by dragging." },
          { title: "Boards & workflows", text: "Scrum and Kanban boards with custom statuses and rules." },
          { title: "Agile reports", text: "Burndown and velocity charts show progress and capacity." },
          { title: "Free for small teams", text: "Up to 10 users on the free plan." } ],
        callout: "Best for: software teams that run real sprints, track estimates and need reports." },
      { type: "table", kicker: "05 · Which one?", title: "Trello or Jira?",
        headers: ["", "Trello", "Jira"],
        rows: [
          ["Model", "Kanban boards: lists and cards", "Scrum and Kanban: backlog, sprints, epics"],
          ["Learning curve", "Minutes", "Days"],
          ["Estimates & reports", "Basic (via Power-Ups)", "Story points, burndown, velocity"],
          ["Free plan", "Up to 10 collaborators per workspace", "Up to 10 users"],
          ["Best for", "Your course project, small teams", "Software teams running sprints"] ] },
      { type: "steps", kicker: "05 · In practice", title: "Set up your project in six steps",
        steps: [
          { title: "Create the board", text: "Scrum template in Jira, or a Trello board with lists." },
          { title: "Write the backlog", text: "Epics and user stories, ordered by value." },
          { title: "Estimate", text: "Story points or T-shirt sizes, as a team." },
          { title: "Plan the sprint", text: "A sprint goal and the stories that achieve it." },
          { title: "Run it daily", text: "Move cards, respect WIP, 15-minute daily." },
          { title: "Review & retro", text: "Show the increment, update the backlog." } ] },
      { type: "rows", kicker: "05 · Definition of done", title: "When is a story really done?", check: true,
        items: [
          { title: "Meets its acceptance criteria" },
          { title: "Code reviewed by a teammate, tests written and passing" },
          { title: "Deployed to a test environment" },
          { title: "Accepted by the product owner, documentation updated" } ] },
      { type: "closing", title: "Agile is a way of learning, not a tool",
        text: "Run the whole life cycle in short sprints, with clear roles and a visible board. Trello and Jira only make it visible." }
    ]
  }
];
