import aiohttp
import pytest
from spanishdict import spanish_word


@pytest.mark.asyncio
async def test_spanish_word_from_spanish():
    expected = {
        "spanish": "<pre><strong>hablar</strong><br></pre><i>Darnley, deberíamos <em>hablar</em> de lo que pasó en el patio.</i><br><i>Bueno, hoy no es el día para <em>hablar</em> de esto.</i>",
        "english": '<pre> 1. (to articulate words)<br>     a. to speak<br>     b. to talk<br> 2. (to converse)<br>     a. to talk<br>     b. to speak<br> 3. (to have a conversation)<br>     a. to speak<br> 4. (to give a speech)<br>     a. to speak<br> 5. (to speak on the phone)<br>     a. to call<br> 6. (to be able to communicate in)<br>     a. to speak<br> 7. (to deal with)<br>     a. to discuss<br>     b. to say<br> 8. (to call)<br> (Argentina)<br> (El Salvador)<br> (Mexico)<br>     a. to phone<br>     hablarse<br> 9. (to have a conversation; often used with "con")<br>     a. to speak to each other<br>     b. to talk to each other<br>     c. to speak to<br>     d. to talk to<br>     e. to be on speaking terms<br></pre><i>Darnley, we should <em>talk about</em> what happened in the courtyard.</i><br><i>Well, today is not the day to <em>talk about</em> this.</i>',
    }
    to_translate = "hablar"
    async with aiohttp.ClientSession() as sesh:
        actual = await spanish_word(sesh, to_translate)

    assert expected == actual


# @pytest.mark.asyncio
# async def test_spanish_word_from_english():
#     expected = {
#         "spanish": "<pre><strong>hablar</strong><br></pre><i>Darnley, deberíamos <em>hablar</em> de lo que pasó en el patio.</i><br><i>Bueno, hoy no es el día para <em>hablar</em> de esto.</i>",
#         "english": "<pre> 1. (to articulate words)<br>     a. to speak<br>     b. to talk<br> 2. (to converse)<br>     a. to ...talk about</em> what happened in the courtyard.</i><br><i>Well, today is not the day to <em>talk about</em> this.</i>",
#     }
#     to_translate = "to speak"
#     async with aiohttp.ClientSession() as sesh:
#         actual = await spanish_word(sesh, to_translate)

#     assert expected == actual
