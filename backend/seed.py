"""
Seed script: populates dummy data for the teacher chatbot POC.

Run with:
    uv run python seed.py

Creates:
  - 1 teacher, 3 students
  - 1 syllabus, 1 cluster, 1 topic
  - 1 rubric (2 constructs: Knowledge/Understanding, Analysis/Argument)
  - 1 class, 1 assignment (WWI causes essay), 1 question
  - 3 submissions with graded responses and inline comments
"""

import asyncio
from datetime import datetime, timezone

from prisma import Prisma


# ---------------------------------------------------------------------------
# Essay texts — each has deliberate argument/factual mistakes for the AI to
# surface when teachers ask about common mistakes across the class.
# ---------------------------------------------------------------------------

ESSAY_ALICE = """\
World War One was caused mainly by the assassination of Archduke Franz Ferdinand \
in Sarajevo in June 1914. This single event triggered the war because it made \
Austria-Hungary very angry. Austria-Hungary then declared war on France, which \
brought the other countries into the conflict through their alliances.

The alliance system was also a cause because countries had promised to help each \
other if attacked. Germany was part of the Triple Alliance with Austria-Hungary \
and Italy. When the war started, all the alliance members had to join in, making \
the conflict much bigger than it would otherwise have been.

In conclusion, the assassination was the most important cause because without it \
the war would never have happened. The other causes like nationalism and militarism \
were less important because countries had been nationalistic for years without \
going to war.
"""

ESSAY_BEN = """\
The main causes of World War One can be remembered using the acronym MAIN: \
Militarism, Alliance systems, Imperialism, and Nationalism. Each of these played \
an important role in bringing about the war.

Militarism meant that European powers were building up large armies and navies. \
Germany in particular had massively expanded its military by 1914. The alliance \
system divided Europe into two armed camps: the Triple Alliance of France, Germany \
and Austria-Hungary, and the Triple Entente of Britain, Russia and Serbia. These \
alliances meant that a local conflict could quickly become a world war.

Imperialism caused rivalry between the great powers as they competed for colonies \
in Africa and Asia. Nationalism was also a powerful force, particularly in the \
Balkans where Slavic peoples wanted independence from Austria-Hungary. The war \
finally broke out in August 1915 when Austria-Hungary declared war on Serbia after \
the assassination of Archduke Franz Ferdinand.
"""

ESSAY_CLARA = """\
World War One had several causes. The most important was militarism, where countries \
spent huge amounts building up their armies and navies. This arms race created tension \
and made war more likely because each country feared the military strength of its \
neighbours.

Nationalism was another key cause. In the Balkans, Serbian nationalism threatened the \
multi-ethnic Austro-Hungarian Empire. The assassination of Franz Ferdinand by Gavrilo \
Princip, a Bosnian-Serb nationalist, gave Austria-Hungary an excuse to crush Serbian \
power once and for all.

Imperialism had nothing to do with the outbreak of war since by 1914 most of Africa \
had already been divided up and there were no more colonial disputes. The alliance \
system was the final cause, turning what could have been a localised Austro-Serbian \
conflict into a global war. Germany's invasion of neutral Belgium to attack France \
brought Britain into the war, completing the chain of alliances.
"""

# ---------------------------------------------------------------------------
# Comments per essay: each is (highlighted_text, comment_content)
# ---------------------------------------------------------------------------

COMMENTS_ALICE = [
    (
        "Austria-Hungary then declared war on France",
        "Factual error: Austria-Hungary declared war on Serbia, not France. "
        "France entered the war because of its alliance with Russia and the German "
        "invasion through Belgium.",
    ),
    (
        "The other causes like nationalism and militarism were less important because "
        "countries had been nationalistic for years without going to war",
        "Weak argument: the fact that nationalism existed before 1914 does not mean it "
        "was unimportant. You need to explain how long-term causes created the conditions "
        "that made war possible once the immediate trigger occurred.",
    ),
    (
        "This single event triggered the war because it made Austria-Hungary very angry",
        "Superficial causal reasoning. 'Being angry' is not a sufficient historical explanation. "
        "Discuss how the assassination activated pre-existing alliance obligations and "
        "Austria-Hungary's strategic decision to use it as a pretext to weaken Serbia.",
    ),
]

COMMENTS_BEN = [
    (
        "the Triple Alliance of France, Germany and Austria-Hungary",
        "Factual error: France was NOT part of the Triple Alliance. The Triple Alliance "
        "consisted of Germany, Austria-Hungary, and Italy. France was part of the Triple "
        "Entente alongside Britain and Russia.",
    ),
    (
        "the war finally broke out in August 1915",
        "Factual error: World War One began in July–August 1914, not 1915. "
        "Austria-Hungary declared war on Serbia on 28 July 1914.",
    ),
    (
        "Triple Entente of Britain, Russia and Serbia",
        "Factual error: Serbia was not a member of the Triple Entente. The Triple Entente "
        "comprised Britain, France, and Russia. Serbia had a separate alliance with Russia.",
    ),
]

# ---------------------------------------------------------------------------
# Nazi Germany essays
# ---------------------------------------------------------------------------

ESSAY_ALICE_NAZI = """\
Adolf Hitler rose to power in Germany because of the Great Depression. When the \
economy collapsed after 1929, millions of Germans lost their jobs and were desperate \
for change. Hitler promised to restore Germany's greatness and provide jobs, so \
people voted for him.

Hitler became Chancellor of Germany in 1933 and immediately made himself dictator \
by passing the Enabling Act, which was supported by a two-thirds majority in the \
Reichstag. He then used the SS and Gestapo to silence all opposition. Jews, \
communists, and other groups were persecuted.

The Treaty of Versailles was also a cause of Hitler's rise because it humiliated \
Germany by forcing it to accept full blame for World War One and pay reparations of \
£6.6 billion. This created resentment that Hitler exploited. Without the Treaty, \
Hitler would never have come to power.

In conclusion, the Great Depression was the main reason Hitler rose to power because \
it created the economic desperation that made Germans willing to support an extreme \
leader. The Weimar Republic was too weak to deal with the crisis.
"""

ESSAY_BEN_NAZI = """\
The rise of Nazi Germany resulted from a combination of factors including the \
weaknesses of the Weimar Republic, economic crisis, and Hitler's personal appeal.

The Weimar Republic was established in 1919 after Germany's defeat in World War One. \
It was always unpopular because it was associated with the humiliation of the \
Treaty of Versailles. The Republic suffered from political instability, with many \
short-lived coalition governments. It also faced a serious challenge from the Munich \
Putsch of 1923, when Hitler tried to overthrow the government. This putsch succeeded \
and brought Hitler to national attention for the first time.

The Great Depression of 1929 was another crucial factor. Unemployment rose to over \
three million by 1932, creating mass suffering and anger at the government. The Nazis \
offered simple solutions: blame the Jews and communists, and promise a strong Germany.

Hitler was appointed Chancellor by President Hindenburg in January 1934. He quickly \
consolidated power through the Reichstag Fire, which he used as an excuse to arrest \
communist leaders, and the Night of the Long Knives, where he eliminated rivals \
within his own party.
"""

ESSAY_CLARA_NAZI = """\
Nazi Germany rose to power primarily because ordinary Germans were suffering and \
looking for someone to blame. Hitler provided clear scapegoats — Jewish people, \
communists, and foreign powers — and promised national revival.

The legacy of World War One was fundamental. Germany had been forced to sign the \
Treaty of Versailles in 1919, accepting the War Guilt Clause and paying massive \
reparations. This caused economic hardship and national humiliation. The Weimar \
Republic, which signed the treaty, was forever seen as the "November criminals" \
who had betrayed Germany.

Propaganda was Hitler's most powerful tool. Joseph Goebbels, as Minister of \
Enlightenment and Propaganda, controlled all media to promote Nazi ideology. \
The Nuremberg Rallies were spectacular displays of Nazi power designed to inspire \
loyalty. Through propaganda, Hitler convinced Germans that he alone could restore \
their national pride.

The Enabling Act of March 1933 was passed after the Reichstag Fire gave Hitler \
the pretext to claim Germany was under communist threat. The Act gave Hitler the \
power to rule by decree for four years without consulting the Reichstag. Since \
communism was the only real threat to Nazi rule, once communists were arrested \
there was no further opposition to Hitler's dictatorship.
"""

COMMENTS_ALICE_NAZI = [
    (
        "the Munich Putsch of 1923, when Hitler tried to overthrow the government. "
        "This putsch succeeded and brought Hitler to national attention",
        "Factual error: the Munich Putsch failed. Hitler was arrested, tried for treason, "
        "and sentenced to five years in prison (serving only nine months). While the putsch "
        "did bring Hitler to national attention, it was a failure, not a success.",
    ),
    (
        "Hitler was appointed Chancellor by President Hindenburg in January 1934",
        "Factual error: Hitler was appointed Chancellor on 30 January 1933, not 1934. "
        "1934 is when Hindenburg died and Hitler merged the roles of Chancellor and President "
        "to become Führer.",
    ),
    (
        "Without the Treaty, Hitler would never have come to power",
        "Overly deterministic argument. While the Treaty of Versailles created conditions "
        "that the Nazis exploited, it is too strong to say Hitler could 'never' have risen "
        "without it. You should acknowledge other enabling factors such as the weaknesses of "
        "the Weimar Republic and Hitler's own political skill.",
    ),
]

COMMENTS_BEN_NAZI = [
    (
        "This putsch succeeded and brought Hitler to national attention for the first time",
        "Factual error: the Munich Putsch of 1923 failed. Police dispersed the marchers "
        "and Hitler was arrested. He was convicted of treason and imprisoned. However, the "
        "trial did give him a national platform, so the second part of your sentence is "
        "partially correct.",
    ),
    (
        "Hitler was appointed Chancellor by President Hindenburg in January 1934",
        "Factual error: Hitler became Chancellor on 30 January 1933, not 1934. "
        "Hindenburg died in August 1934, after which Hitler combined the offices of "
        "Chancellor and President.",
    ),
    (
        "Since communism was the only real threat to Nazi rule, once communists were "
        "arrested there was no further opposition to Hitler's dictatorship",
        "Weak argument: this ignores significant other sources of potential opposition, "
        "including the SA (addressed in the Night of the Long Knives), conservative "
        "politicians, the Church, and later resistance groups. The claim is too absolute.",
    ),
]

COMMENTS_CLARA_NAZI = [
    (
        "Since communism was the only real threat to Nazi rule, once communists were "
        "arrested there was no further opposition to Hitler's dictatorship",
        "Inaccurate and overstated. Opposition to Nazi rule was not limited to communists. "
        "The SA posed an internal threat (Night of the Long Knives, 1934), the Catholic "
        "Church resisted certain Nazi policies, and various resistance groups operated "
        "throughout the regime. Revise this claim.",
    ),
    (
        "Joseph Goebbels, as Minister of Enlightenment and Propaganda, controlled all media",
        "Slight overstatement: while Goebbels exerted extensive control through the Reich "
        "Chamber of Culture, 'all media' is an exaggeration. Some private and church "
        "publications continued, though under significant restriction. Be more precise "
        "in your claims.",
    ),
]

COMMENTS_CLARA = [
    (
        "Imperialism had nothing to do with the outbreak of war since by 1914 most of "
        "Africa had already been divided up and there were no more colonial disputes",
        "Incorrect argument: imperial rivalry remained a significant source of tension even "
        "after the Scramble for Africa. The Moroccan Crises of 1905 and 1911 nearly led to "
        "war between France and Germany over colonial interests. Imperial competition also "
        "fuelled the arms race and nationalist rivalries that contributed to the war.",
    ),
    (
        "Germany's invasion of neutral Belgium to attack France brought Britain into the war, "
        "completing the chain of alliances",
        "Britain's entry was not purely an alliance obligation — Britain had no formal alliance "
        "with France or Russia. Britain entered because of the 1839 Treaty of London guaranteeing "
        "Belgian neutrality, and broader strategic concerns about German dominance of the continent. "
        "Clarify this distinction.",
    ),
]


async def main() -> None:
    db = Prisma()
    await db.connect()

    print("Seeding database...")

    # Idempotency check — skip if already seeded
    existing = await db.user.find_unique(where={"id": "seed_teacher_id"})
    if existing:
        print("Database already seeded — skipping.")
        await db.disconnect()
        return

    # ------------------------------------------------------------------
    # Syllabus
    # ------------------------------------------------------------------
    syllabus = await db.syllabus.create(
        data={
            "name": "Lower Secondary Humanities",
            "subject": "geography",
            "levels": ["sec3"],
            "order": 1,
        }
    )
    print(f"  Created syllabus: {syllabus.id}")

    # ------------------------------------------------------------------
    # Cluster + OrderedCluster + Topic
    # ------------------------------------------------------------------
    cluster = await db.cluster.create(data={"name": "Global Conflicts"})
    await db.orderedcluster.create(
        data={
            "clusterId": cluster.id,
            "syllabusId": syllabus.id,
            "order": 1,
        }
    )
    topic = await db.topic.create(
        data={
            "name": "Causes of World War One",
            "content": "Explore the long-term and short-term causes of WWI including MAIN factors.",
            "order": 1,
            "clusterId": cluster.id,
        }
    )
    print(f"  Created topic: {topic.id}")

    # ------------------------------------------------------------------
    # Rubric: 2 constructs, each with 4 bands
    # ------------------------------------------------------------------
    rubric = await db.rubric.create(
        data={"name": "History Essay Rubric", "description": "For source-based and essay questions."}
    )

    construct_knowledge = await db.construct.create(
        data={
            "name": "Knowledge & Understanding",
            "description": "Accuracy and breadth of factual knowledge about the causes of WWI.",
            "order": 1,
            "rubricId": rubric.id,
        }
    )
    for level, mn, mx, descriptor in [
        (1, 0, 2, "Little or no relevant factual knowledge. Major factual errors present."),
        (2, 3, 5, "Some relevant knowledge with minor factual errors or gaps."),
        (3, 6, 8, "Mostly accurate knowledge of key causes with only minor errors."),
        (4, 9, 10, "Accurate and detailed knowledge of multiple causes with no significant errors."),
    ]:
        await db.band.create(
            data={
                "level": level,
                "minMarks": mn,
                "maxMarks": mx,
                "descriptor": descriptor,
                "constructId": construct_knowledge.id,
            }
        )

    construct_analysis = await db.construct.create(
        data={
            "name": "Analysis & Argument",
            "description": "Quality of causal reasoning and argument structure.",
            "order": 2,
            "rubricId": rubric.id,
        }
    )
    for level, mn, mx, descriptor in [
        (1, 0, 2, "No clear argument. Causes listed without explanation or connection."),
        (2, 3, 5, "Basic causal links made but argument is superficial or one-sided."),
        (3, 6, 8, "Clear argument with explanation of how causes connect, though analysis could be deeper."),
        (4, 9, 10, "Sustained, sophisticated argument linking multiple causes with well-supported causal reasoning."),
    ]:
        await db.band.create(
            data={
                "level": level,
                "minMarks": mn,
                "maxMarks": mx,
                "descriptor": descriptor,
                "constructId": construct_analysis.id,
            }
        )

    print(f"  Created rubric with 2 constructs: {rubric.id}")

    # ------------------------------------------------------------------
    # Teacher
    # ------------------------------------------------------------------
    teacher = await db.user.create(
        data={
            "id": "seed_teacher_id",
            "email": "ms.lim@school.edu.sg",
            "name": "Ms Lim Wei Ling",
            "role": "teacher",
        }
    )
    print(f"  Created teacher: {teacher.id}  ({teacher.email})")

    # ------------------------------------------------------------------
    # Students
    # ------------------------------------------------------------------
    alice = await db.user.create(
        data={"email": "alice.chen@student.edu.sg", "name": "Alice Chen", "role": "student"}
    )
    ben = await db.user.create(
        data={"email": "ben.tan@student.edu.sg", "name": "Ben Tan", "role": "student"}
    )
    clara = await db.user.create(
        data={"email": "clara.wong@student.edu.sg", "name": "Clara Wong", "role": "student"}
    )
    students = [alice, ben, clara]
    print(f"  Created 3 students: {alice.name}, {ben.name}, {clara.name}")

    # ------------------------------------------------------------------
    # Class
    # ------------------------------------------------------------------
    school_class = await db.schoolclass.create(
        data={
            "code": "HUM-3A-2024",
            "name": "Secondary 3A Humanities",
            "level": "sec3",
            "syllabusId": syllabus.id,
            "teachers": {"connect": [{"id": teacher.id}]},
            "students": {"connect": [{"id": s.id} for s in students]},
        }
    )
    print(f"  Created class: {school_class.id}  ({school_class.name})")

    # ------------------------------------------------------------------
    # Assignment
    # ------------------------------------------------------------------
    assignment = await db.assignment.create(
        data={
            "title": "Causes of World War One Essay",
            "description": (
                "Write an essay explaining the main causes of World War One. "
                "You should discuss at least three causes and explain how they "
                "contributed to the outbreak of war in 1914."
            ),
            "level": "sec3",
            "dueDate": datetime(2024, 10, 15, 23, 59, tzinfo=timezone.utc),
            "createdById": teacher.id,
            "syllabusId": syllabus.id,
            "classes": {"connect": [{"id": school_class.id}]},
        }
    )
    print(f"  Created assignment: {assignment.id}")

    # ------------------------------------------------------------------
    # Question
    # ------------------------------------------------------------------
    question = await db.question.create(
        data={
            "questionNumber": "1",
            "questionPrompt": (
                "Explain the main causes of World War One. In your answer, "
                "you should consider both long-term and short-term causes, "
                "and explain how these factors combined to bring about the war."
            ),
            "assignmentId": assignment.id,
            "rubricId": rubric.id,
            "topics": {"connect": [{"id": topic.id}]},
        }
    )
    print(f"  Created question: {question.id}")

    # ------------------------------------------------------------------
    # Submissions, responses, comments, and grades
    # ------------------------------------------------------------------
    # Band IDs for grading: fetch them after creation
    bands_knowledge = await db.band.find_many(
        where={"constructId": construct_knowledge.id}, order={"level": "asc"}
    )
    bands_analysis = await db.band.find_many(
        where={"constructId": construct_analysis.id}, order={"level": "asc"}
    )

    # (student, essay, comments, knowledge_band_idx, analysis_band_idx, k_marks, a_marks, feedback)
    submission_data = [
        (
            alice,
            ESSAY_ALICE,
            COMMENTS_ALICE,
            1,  # band index (0-based) for knowledge → band level 2
            1,  # band index for analysis → band level 2
            4,
            3,
            "Alice demonstrates some understanding of the alliance system but makes a "
            "significant factual error regarding Austria-Hungary's declaration of war. "
            "The argument oversimplifies causation by dismissing long-term factors. "
            "Work on connecting short-term triggers to long-term underlying causes.",
        ),
        (
            ben,
            ESSAY_BEN,
            COMMENTS_BEN,
            0,  # band level 1 — multiple factual errors
            2,  # band level 3 — good structure despite errors
            2,
            6,
            "Ben shows good analytical structure using the MAIN framework, but has "
            "made several serious factual errors including the wrong members of the "
            "Triple Alliance and an incorrect start date for the war. The framework "
            "is a strength — the factual accuracy needs significant improvement.",
        ),
        (
            clara,
            ESSAY_CLARA,
            COMMENTS_CLARA,
            2,  # band level 3
            2,  # band level 3
            7,
            7,
            "Clara presents a well-structured essay with generally accurate knowledge. "
            "The main weakness is the dismissal of imperialism as a cause, which is "
            "historically inaccurate. The explanation of Britain's entry also needs "
            "more precision. Strong foundation — refine the argument on imperialism.",
        ),
    ]

    for student, essay, comments, k_band_idx, a_band_idx, k_marks, a_marks, feedback in submission_data:
        submission = await db.submission.create(
            data={
                "isMarked": True,
                "returnedAt": datetime(2024, 10, 22, tzinfo=timezone.utc),
                "assignmentId": assignment.id,
                "studentId": student.id,
                "classId": school_class.id,
            }
        )

        qr = await db.questionresponse.create(
            data={
                "content": essay,
                "questionId": question.id,
                "submissionId": submission.id,
                "overallFeedback": feedback,
            }
        )

        # Inline comments
        for highlighted, comment_text in comments:
            # Find the index of the highlighted text in the essay for startIndex/endIndex
            idx = essay.find(highlighted)
            start = idx if idx != -1 else 0
            end = start + len(highlighted)
            await db.comment.create(
                data={
                    "content": comment_text,
                    "highlightedText": highlighted,
                    "startIndex": start,
                    "endIndex": end,
                    "questionResponseId": qr.id,
                    "status": "approved",
                }
            )

        # Construct grades
        await db.constructgrade.create(
            data={
                "constructId": construct_knowledge.id,
                "bandId": bands_knowledge[k_band_idx].id,
                "marksAwarded": k_marks,
                "explanation": f"See overall feedback.",
                "questionResponseId": qr.id,
            }
        )
        await db.constructgrade.create(
            data={
                "constructId": construct_analysis.id,
                "bandId": bands_analysis[a_band_idx].id,
                "marksAwarded": a_marks,
                "explanation": f"See overall feedback.",
                "questionResponseId": qr.id,
            }
        )

        print(f"  Created submission for {student.name} (K:{k_marks}/10, A:{a_marks}/10)")

    # ------------------------------------------------------------------
    # Assignment 2: The Rise of Nazi Germany
    # ------------------------------------------------------------------
    assignment2 = await db.assignment.create(
        data={
            "title": "The Rise of Nazi Germany",
            "description": (
                "Write an essay explaining how and why the Nazi Party rose to power "
                "in Germany between 1919 and 1934. You should consider the role of "
                "economic factors, political weaknesses, and Hitler's own actions."
            ),
            "level": "sec3",
            "dueDate": datetime(2024, 11, 12, 23, 59, tzinfo=timezone.utc),
            "createdById": teacher.id,
            "syllabusId": syllabus.id,
            "classes": {"connect": [{"id": school_class.id}]},
        }
    )

    topic2 = await db.topic.create(
        data={
            "name": "The Rise of Nazi Germany",
            "content": "Examine the political, economic, and social conditions that enabled Hitler's rise to power.",
            "order": 2,
            "clusterId": cluster.id,
        }
    )

    question2 = await db.question.create(
        data={
            "questionNumber": "1",
            "questionPrompt": (
                "Explain how Hitler and the Nazi Party rose to power in Germany between 1919 and 1934. "
                "In your answer, consider the weaknesses of the Weimar Republic, the impact of economic "
                "crises, and the methods Hitler used to consolidate power."
            ),
            "assignmentId": assignment2.id,
            "rubricId": rubric.id,
            "topics": {"connect": [{"id": topic2.id}]},
        }
    )
    print(f"  Created assignment 2: {assignment2.id}")

    # Fetch bands again (same rubric, same constructs)
    submission_data2 = [
        (
            alice,
            ESSAY_ALICE_NAZI,
            COMMENTS_ALICE_NAZI,
            1,  # band level 2 — some knowledge, notable errors
            1,  # band level 2 — basic argument
            4,
            4,
            "Alice identifies the key factors but makes a critical factual error about the "
            "Munich Putsch succeeding, and gives the wrong year for Hitler's appointment as "
            "Chancellor. The conclusion is too deterministic. Review the chronology carefully "
            "and avoid absolute causal claims.",
        ),
        (
            ben,
            ESSAY_BEN_NAZI,
            COMMENTS_BEN_NAZI,
            1,  # band level 2
            2,  # band level 3 — reasonable structure
            4,
            6,
            "Ben demonstrates a reasonable analytical structure, covering Weimar weaknesses, "
            "the Depression, and Hitler's consolidation of power. However, the Munich Putsch "
            "is described as a success (it failed), and the year of Hitler's appointment is "
            "wrong. Fix these factual errors — they undermine an otherwise competent essay.",
        ),
        (
            clara,
            ESSAY_CLARA_NAZI,
            COMMENTS_CLARA_NAZI,
            2,  # band level 3
            2,  # band level 3
            7,
            6,
            "Clara writes a well-structured essay with strong coverage of propaganda and the "
            "Treaty of Versailles. The main weaknesses are an overstated claim about communist "
            "opposition being the 'only' threat, and a slight exaggeration about Goebbels "
            "controlling 'all' media. Precision in claims will strengthen the argument.",
        ),
    ]

    for student, essay, comments, k_band_idx, a_band_idx, k_marks, a_marks, feedback in submission_data2:
        submission = await db.submission.create(
            data={
                "isMarked": True,
                "returnedAt": datetime(2024, 11, 19, tzinfo=timezone.utc),
                "assignmentId": assignment2.id,
                "studentId": student.id,
                "classId": school_class.id,
            }
        )

        qr = await db.questionresponse.create(
            data={
                "content": essay,
                "questionId": question2.id,
                "submissionId": submission.id,
                "overallFeedback": feedback,
            }
        )

        for highlighted, comment_text in comments:
            idx = essay.find(highlighted)
            start = idx if idx != -1 else 0
            end = start + len(highlighted)
            await db.comment.create(
                data={
                    "content": comment_text,
                    "highlightedText": highlighted,
                    "startIndex": start,
                    "endIndex": end,
                    "questionResponseId": qr.id,
                    "status": "approved",
                }
            )

        await db.constructgrade.create(
            data={
                "constructId": construct_knowledge.id,
                "bandId": bands_knowledge[k_band_idx].id,
                "marksAwarded": k_marks,
                "explanation": "See overall feedback.",
                "questionResponseId": qr.id,
            }
        )
        await db.constructgrade.create(
            data={
                "constructId": construct_analysis.id,
                "bandId": bands_analysis[a_band_idx].id,
                "marksAwarded": a_marks,
                "explanation": "See overall feedback.",
                "questionResponseId": qr.id,
            }
        )

        print(f"  Created submission for {student.name} (K:{k_marks}/10, A:{a_marks}/10)")

    print()
    print("Seed complete!")
    print()
    print(f"Teacher ID (use in .env TEACHER_USER_ID): {teacher.id}")
    print(f"Assignment 1 ID (WWI): {assignment.id}")
    print(f"Assignment 2 ID (Nazi Germany): {assignment2.id}")

    await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
