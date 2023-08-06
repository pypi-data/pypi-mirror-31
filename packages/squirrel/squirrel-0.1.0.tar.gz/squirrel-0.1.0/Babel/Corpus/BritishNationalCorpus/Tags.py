####################################################################################################
#
# Babel - An Electronic Document Management System
# Copyright (C) 2014 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
####################################################################################################

####################################################################################################
#
# British National Corpus Part-of-speech tags
#
# Extracted from the BNC Manual
#
####################################################################################################

from ..Tags import TagsAbc

####################################################################################################

class Tags(TagsAbc):

    __language__ = 'en'

    __tags__ = {
        'AJ0': """adjective (general or positive) e.g. good, old""",

        'AJC': """comparative adjective e.g. better, older""",

        'AJS': """superlative adjective, e.g. best, oldest""",

        'AT0': """article, e.g. the, a, an, no . Note the inclusion of no: articles are defined"""
        """ as determiners which typically begin a noun phrase but cannot appear as its head.""",

        'AV0': """adverb (general, not sub-classified as AVP or AVQ), e.g. often, well, longer, furthest."""
        """ Note that adverbs, unlike adjectives, are not tagged as positive, comparative, or superlative."""
        """ This is because of the relative rarity of comparative or superlative forms.""",

        'AVP': """adverb particle, e.g. up, off, out. This tag is used for all prepositional adverbs,"""
        """ whether or not they are used idiomatically in phrasal verbs such as "Come out here","""
        """ or "I can't hold out any longer".""",

        'AVQ': """wh-adverb, e.g. when, how, why. The same tag is used whether the word is used interrogatively"""
        """ or to introduce a relative clause.""",

        'CJC': """coordinating conjunction, e.g. and, or, but.""",

        'CJS': """subordinating conjunction, e.g. although, when.""",

        'CJT': """the subordinating conjunction that, when introducing a relative clause,"""
        """ as in "the day that follows Christmas". Some theories treat that here as a relative pronoun;"""
        """ others as a conjunction. We have adopted the latter analysis.""",

        'CRD': """cardinal numeral, e.g. one, 3, fifty-five, 6609.""",

        'DPS': """possessive determiner form, e.g. your, their, his.""",

        'DT0': """general determiner: a determiner which is not a DTQ e.g. this both in "This is my house" and"""
        """ "This house is mine". A determiner is defined as a word which typically occurs either as"""
        """ the first word in a noun phrase, or as the head of a noun phrase.""",

        'DTQ': """wh-determiner, e.g. which, what, whose, which. The same tag is used whether the word"""
        """ is used interrogatively or to introduce a relative clause.""",

        'EX0': """existential there, the word thereappearing in the constructions "there is...", "there are ...".""",

        'ITJ': """interjection or other isolate, e.g. oh, yes, mhm, wow.""",

        'NN0': """common noun, neutral for number, e.g. aircraft, data, committee. Singular collective nouns"""
        """ such as committee take this tag on the grounds that they can be followed by either a singular or a plural verb.""",

        'NN1': """singular common noun, e.g. pencil, goose, time, revelation.""",

        'NN2': """plural common noun, e.g. pencils, geese, times, revelations.""",

        'NP0': """proper noun, e.g. London, Michael, Mars, IBM. Note that no distinction is made for number"""
        """ in the case of proper nouns, since plural proper names are a comparative rarity.""",

        'ORD': """ordinal numeral, e.g. first, sixth, 77th, next, last. No distinction is made between ordinals"""
        """ used in nominal and adverbial roles. next and last are included in this category, as general ordinals.""",

        'PNI': """indefinite pronoun, e.g. none, everything, one (pronoun), nobody. This tag is applied to words"""
        """ which always function as heads of noun phrases. Words like some and these, which can also """
        """ occur before a noun head in an article-like function, are tagged as determiners, DT0 or AT0.""",

        'PNP': """personal pronoun, e.g. I, you, them, ours. Note that possessive pronouns"""
        """ such as ours and theirs are included in this category.""",

        'PNQ': """wh-pronoun, e.g. who, whoever, whom. The same tag is used whether the word is used"""
        """ interrogatively or to introduce a relative clause.""",

        'PNX': """reflexive pronoun, e.g. myself, yourself, itself, ourselves.""",

        'POS': """the possessive or genitive marker 's or '. Note that this marker is tagged as a distinct word."""
        """ For example, "Peter's or someone else's" is tagged Peter's or someone else's ]]>""",

        'PRF': """the preposition of. This word has a special tag of its own,"""
        """ because of its high frequency and its almost exclusively postnominal function.""",

        'PRP': """preposition, other than of, e.g. about, at, in, on behalf of, with."""
        """ Note that prepositional phrases like on behalf of or in spite of are treated as single words.""",

        'TO0': """the infinitive marker to.""",

        'UNC': """"unclassified" items which are not appropriately classified as items of the English lexicon."""
        """ Examples include foreign (non-English) words; special typographical symbols; formulae;"""
        """ hesitation fillers such as errm in spoken language.""",

        'VBB': """the present tense forms of the verb be, except for is or 's am, are 'm, 're, be """
        """ (subjunctive or imperative), ai (as in ain't).""",

        'VBD': """the past tense forms of the verb be, was, were.""",

        'VBG': """-ing form of the verb be, being.""",

        'VBI': """the infinitive form of the verb be, be.""",

        'VBN': """the past participle form of the verb be, been""",

        'VBZ': """the -s form of the verb be, is, 's.""",

        'VDB': """the finite base form of the verb do, do.""",

        'VDD': """the past tense form of the verb do, did.""",

        'VDG': """the -ing form of the verb do, doing.""",

        'VDI': """the infinitive form of the verb do, do.""",

        'VDN': """the past participle form of the verb do, done.""",

        'VDZ': """the -s form of the verb do, does.""",

        'VHB': """the finite base form of the verb have, have, 've.""",

        'VHD': """the past tense form of the verb have, had, 'd.""",

        'VHG': """the -ing form of the verb have, having.""",

        'VHI': """the infinitive form of the verb have, have.""",

        'VHN': """the past participle form of the verb have, had.""",

        'VHZ': """the -s form of the verb have, has, 's.""",

        'VM0': """modal auxiliary verb, e.g. can, could, will, 'll, 'd, wo (as in won't)""",

        'VVB': """the finite base form of lexical verbs, e.g. forget, send, live, return."""
        """This tag is used for imperatives and the present subjunctive forms, but not for the infinitive (VVI).""",

        'VVD': """the past tense form of lexical verbs, e.g. forgot, sent, lived, returned.""",

        'VVG': """the -ing form of lexical verbs, e.g. forgetting, sending, living, returning.""",

        'VVI': """the infinitive form of lexical verbs , e.g. forget, send, live, return.""",

        'VVN': """the past participle form of lexical verbs, e.g. forgotten, sent, lived, returned.""",

        'VVZ': """the -s form of lexical verbs, e.g. forgets, sends, lives, returns.""",

        'XX0': """the negative particle not or n't.""",

        'ZZ0': """alphabetical symbols, e.g. A, a, B, b, c, d.""",

        # The following portmanteau tags are used to indicate where the CLAWS system has indicated an
        # uncertainty between two possible analyses:

        'AJ0-AV0': """adjective or adverb""",

        'AJ0-NN1': """adjective or singular common noun""",

        'AJ0-VVD': """adjective or past tense verb""",

        'AJ0-VVG': """adjective or -ing form of the verb""",

        'AJ0-VVN': """adjective or past participle""",

        'AVP-PRP': """adverb particle or preposition""",

        'AVQ-CJS': """wh-adverb or subordinating conjunction""",

        'CJS-PRP': """subordinating conjunction or preposition""",

        'CJT-DT0': """that as conjunction or determiner""",

        'CRD-PNI': """one as number or pronoun""",

        'NN1-NP0': """singular common noun or proper noun""",

        'NN1-VVB': """singular common noun or base verb form""",

        'NN1-VVG': """singular common noun or -ing form of the verb""",

        'NN2-VVZ': """plural noun or -s form of lexical verb""",

        'VVD-VVN': """past tense verb or past participle""",

        # The following codes are used with c elements only:

        'PUL': """left bracket (i.e. ( or [ )""",

        'PUN': """any mark of separation ( . ! , : ; - ? ... )""",

        'PUQ': """quotation mark ( ` ' `` '' )""",

        'PUR': """right bracket (i.e. ) or ] )""",

        # Note that some punctuation marks (notably long dashes and ellipses) are not tagged as such in
        # the corpus, but appear simply as entity references.
    }

    __noun_tags__ = ('NN1', 'NN1-NP0', 'NN1-VVB', 'NN1-VVG', 'NN2', 'NN2-VVZ', 'NP0')
