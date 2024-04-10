import asyncio
from pyppeteer import launch


async def main():
    browser = await launch()
    page = await browser.newPage()
    await page.goto("https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6002118/")
    await page.screenshot({"path": "example.png"})
    content = await page.evaluate('() => document.querySelector("*").innerText')
    with open("example.txt", "w") as f:
        f.write(content)
    await browser.close()


asyncio.run(main())
