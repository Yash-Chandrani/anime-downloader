from anime_downloader.sites.anime import Anime, AnimeEpisode, SearchResult
from anime_downloader.sites import helpers


def parse_search_page(soup):
    results = soup.select('ul.thumb > li > a')
    return [
            SearchResult(
                title=x['title'],
                url=x['href'],
                poster=x.find('img')['src']
            )
            for x in results
        ]


class TenshiMoe(Anime, sitename='tenshi.moe'):

    sitename = 'tenshi.moe'

    @classmethod
    def search(cls, query):
        soup = helpers.soupify(
            helpers.get(
                'https://tenshi.moe/anime',
                params={'q': query},
                cookies={'loop-view': 'thumb'}
            )
        )

        results = parse_search_page(soup)

        while soup.select_one(".pagination"):
            link = soup.select_one('a.page-link[rel="next"]')
            if link:
                soup = helpers.soupify(
                    helpers.get(
                        link['href'],
                        cookies={'loop-view': 'thumb'}
                    )
                )
                results.extend(parse_search_page(soup))
            else:
                break

        return results

    def _scrape_episodes(self):
        soup = helpers.soupify(helpers.get(self.url))
        eps = soup.select(
            'li[class*="episode"] > a'
        )
        eps = [x['href'] for x in eps]
        return eps

    def _scrape_metadata(self):
        soup = helpers.soupify(helpers.get(self.url).text)
        self.title = soup.title.text.split('—')[0].strip()


class TenshiMoeEpisode(AnimeEpisode, sitename='tenshi.moe'):
    QUALITIES = ['360p', '480p', '720p', '1080p']

    def _get_sources(self):
        soup = helpers.soupify(helpers.get(self.url))
        soup = soup.select_one('.embed-responsive > iframe')

        mp4moe = helpers.soupify(helpers.get(soup.get('src'), referer=self.url))
        mp4moe = mp4moe.select_one('video#player')
        qualities_ = [x.get("title") for x in mp4moe.select('source')]
        sources = [
            ('no_extractor', x.get('src'))
            for x in mp4moe.select('source')
        ]

        if self.quality in qualities_:
            return [sources[qualities_.index(self.quality)]]

