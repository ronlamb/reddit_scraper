# Convert filename to https://www.redgifs.com/watch/brownembellishedbandicoot
import logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

import os
import pathlib

import requests

"""
Class RegGifs
Handles processing files from redgifs.com.  

"""
class RedGifs:
    def __init__(self):
        pass

    def get_filename(self,url):
        fragment_removed = url.split("#")[0]  # keep to left of first #
        query_string_removed = fragment_removed.split("?")[0]
        scheme_removed = query_string_removed.split("://")[-1].split(":")[-1]
        if scheme_removed.find("/") == -1:
            return ""
        return os.path.basename(scheme_removed)

    # Get's the actual file from a watch url
    # TODO: Replace with call to redgifs API
    def get_actual_file(self, url):
        filename = self.get_filename(url)
        stem = pathlib.Path(filename).stem

        # Get the page from watch
        watch_url = f"https://www.redgifs.com/watch/{stem}"
        req =  requests.get(watch_url)

        # Return the actual url to the file
        if req.status_code == 200:
            return self.parse_content(req.text)
        else:
            return None

    def _parse_url(self, iurl, itext):
        text = itext
        loc = text.find(iurl)
        text = text[loc:]

        # Get the URL between the double quotes
        start = text.find('"')
        text = text[start+1:]
        end = text.find('"')
        url = text[:end]

        # strip off -small and replace it with -large
        ext = pathlib.Path(url).suffix
        small = f"-small{ext}"
        if url.endswith(small):
            url = url[:len(url)-len(small)] + f"-large{ext}"
            return url

        # Next try to find /files/
        loc = text.find('/files/')
        text = text[loc+7:]
        quot = text.find('"')

        fname = text[:quot]
        if "-large" in fname:
            return f"https://files.redgifs.com/{fname}"

        return None

    def _parse_url2(self, iurl, itext):
        text = itext
        loc = text.find(iurl)
        text = text[loc:]

        # Get the URL between the double quotes
        # start = text.find('"')
        # text = text[start+1:]
        end = text.find('"')
        url = text[:end]

        # strip off -small and replace it with -large
        ext = pathlib.Path(url).suffix
        small = f"-small{ext}"
        if url.endswith(small):
            url = url[:len(url)-len(small)] + f"-large{ext}"
            return url

        # # Next try to find /files/
        # loc = text.find('/files/')
        # text = text[loc+7:]
        # quot = text.find('"')
        #
        # fname = text[:quot]
        # if "-large" in fname:
        #     return f"https://files.redgifs.com/{fname}"

        return None

    # Simple function that finds text
    #   href="https://files.redgifs.com/<filename>-small.<ext>"
    #   And converts it to ="https://files.redgifs.com/<filename>-large.<ext>"
    def parse_content(self, itext):
        # log.info(f"Text:{itext}")
        fname = self._parse_url("https://files.redgifs.com", itext)
        if fname is None:
            fname = self._parse_url2("https://media.redgifs.com", itext)

        return fname
        # text = itext
        # loc = text.find('href="https://files.redgifs.com")
        # text = text[loc:]
        #
        # log.info(f"Text:{text}")
        # # Get the URL between the double quotes
        # start = text.find('"')
        # text = text[start+1:]
        # end = text.find('"')
        # url = text[:end]
        #
        # # strip off -small and replace it with -large
        # ext = pathlib.Path(url).suffix
        # small = f"-small{ext}"
        # if url.endswith(small):
        #     url = url[:len(url)-len(small)] + f"-large{ext}"
        #     return url
        #
        # # Next try to find /files/
        # loc = text.find('/files/')
        # text = text[loc+7:]
        # quot = text.find('"')
        #
        # fname = text[:quot]
        # if "-large" in fname:
        #     return f"https://files.redgifs.com/{fname}"
        #
        # fname = self.parse_meta(itext)
        # return fname
        # return None

if __name__ == '__main__':
    red = RedGifs()
    # red.get_actual_file("https://i.redgifs.com/i/bubblydecentsidewinder.jpg")
    red.parse_content("""<!doctype html><html lang="en" translate="no"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1"><meta http-equiv="X-UA-Compatible" content="IE=Edge"><link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png"><link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png"><link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png"><link rel="manifest" crossorigin="use-credentials" href="/site.webmanifest"><link rel="mask-icon" href="/safari-pinned-tab.svg" color="#e5194d"><meta name="msapplication-TileColor" content="#161617"><meta name="theme-color" content="#161617"><meta name="apple-mobile-web-app-status-bar-style" content="#161617"><link rel="preconnect" href="https://thumbs54.redgifs.com"><link rel="preconnect" href="https://thumbs56.redgifs.com"><link rel="preconnect" href="https://userpic.redgifs.com/"><style>*{box-sizing:border-box;padding:0;margin:0;text-transform:none!important;font-family:Poppins,sans-serif}body{margin:0;font-weight:500;-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;background-color:#0b0b28;color:#fff;min-width:320px}li{list-style-type:none;list-style-position:inside}button{cursor:pointer;box-sizing:border-box;text-align:center}</style><style>@font-face{font-display:swap;font-family:Poppins;font-style:normal;font-weight:400;src:url('/assets/fonts/poppins-v20-latin_latin-ext-regular.woff2') format('woff2')}@font-face{font-display:swap;font-family:Poppins;font-style:normal;font-weight:500;src:url('/assets/fonts/poppins-v20-latin_latin-ext-500.woff2') format('woff2')}@font-face{font-display:swap;font-family:Poppins;font-style:normal;font-weight:600;src:url('/assets/fonts/poppins-v21-latin_latin-ext-600.woff2') format('woff2')}</style><script>if(!location.search.includes("disable_ga=yes")){(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start': new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0], j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src= 'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer','GTM-5SCT9DN');}</script><script>setTimeout(function () {if (Math.random() >= 0.001) {return;}(function(n,i,v,r,s,c,x,z){x=window.AwsRumClient={q:[],n:n,i:i,v:v,r:r,c:c};window[n]=function(c,p){x.q.push({c:c,p:p});};z=document.createElement('script');z.async=true;z.src=s;document.head.insertBefore(z,document.head.getElementsByTagName('script')[0]);})('cwr', '6dde6311-b802-409f-afb1-9ba4cf23b553', '1.0.0', 'us-east-1', 'https://client.rum.us-east-1.amazonaws.com/1.14.0/cwr.js', {sessionSampleRate: 1, guestRoleArn: "arn:aws:iam::488108494299:role/RUM-Monitor-us-east-1-488108494299-9466386438361-Unauth", identityPoolId: "us-east-1:138bec98-05c6-4e5c-91ba-126c5742904a", endpoint: "https://dataplane.rum.us-east-1.amazonaws.com", telemetries: ["performance"], allowCookies: false, enableXRay: false});}, 3000);</script><script type="module" crossorigin src="/static/index-Bz9JepEV.js"></script><link rel="modulepreload" crossorigin href="/static/amplitude-vendor-BjEHwcZz.js"><link rel="modulepreload" crossorigin href="/static/vendor-Y9LGTdLU.js"><link rel="modulepreload" crossorigin href="/static/recombee-vendor-Dat2Ic0e.js"><link rel="stylesheet" crossorigin href="/static/index-Bez8gLAt.css"><link rel="canonical" href="https://www.redgifs.com/watch/bubblydecentsidewinder" /><title>Eva Angelina Fake Boobs Fake Tits Porn Image by useme4porn</title><meta name="keywords" content="Eva Angelina, Fake Boobs, Fake Tits" /><link rel="alternate" type="application/json+oembed" href="https://api.redgifs.com/v1/oembed?url=https%3A%2F%2Fwww.redgifs.com%2Fwatch%2Fbubblydecentsidewinder" title="RedGIFs"><link rel="preload" as="image" href="https://files.redgifs.com/BubblyDecentSidewinder-small.jpg" /><meta property="og:title" content="Eva Angelina Fake Boobs Fake Tits Porn Image by useme4porn" /><meta property="og:site_name" content="RedGIFs" /><meta property="og:type" content="image" /><meta property="og:description" content="Enjoy this Eva Angelina porn BubblyDecentSidewinder from useme4porn. Sign up for free and start building your porn collection from the millions of GIFs and images free on RedGIFs"><meta property="og:image:url" content="https://api.redgifs.com/v2/gifs/bubblydecentsidewinder/files/BubblyDecentSidewinder-large.jpg"><meta property="og:image:secure_url" content="https://api.redgifs.com/v2/gifs/bubblydecentsidewinder/files/BubblyDecentSidewinder-large.jpg"><meta property="og:image:type" content="image/jpeg"><meta property="og:image:width" content="2048"><meta property="og:image:height" content="3078"><meta property="og:image:url" content="https://api.redgifs.com/v2/gifs/bubblydecentsidewinder/files/BubblyDecentSidewinder-medium.jpg"><meta property="og:image:secure_url" content="https://api.redgifs.com/v2/gifs/bubblydecentsidewinder/files/BubblyDecentSidewinder-medium.jpg"><meta property="og:image:type" content="image/jpeg"><meta property="og:image:width" content="800"><meta property="og:image:height" content="1202"><meta property="og:image:url" content="https://api.redgifs.com/v2/gifs/bubblydecentsidewinder/files/BubblyDecentSidewinder-small.jpg"><meta property="og:image:secure_url" content="https://api.redgifs.com/v2/gifs/bubblydecentsidewinder/files/BubblyDecentSidewinder-small.jpg"><meta property="og:image:type" content="image/jpeg"><meta property="og:image:width" content="360"><meta property="og:image:height" content="541"><meta name="twitter:account_id" content="1186453478928867329" /><meta name="twitter:site" content="@RedGifsOfficial" /><meta name="twitter:creator" content="@RedGifsOfficial" /><meta name="twitter:domain" content="redgifs.com" /><meta name="twitter:title" content="Eva Angelina Fake Boobs Fake Tits Porn Image by useme4porn | RedGIFs" /><meta name="twitter:card" content="summary_large_image" /><meta name="twitter:description" content="See this photo on RedGIFs.com, the best porn GIFs site. RedGIFs is the leading free porn GIFs site in the world. Browse millions of hardcore sex GIFs and the NEWEST porn videos every day!" /><meta name="twitter:url" content="https://www.redgifs.com/watch/bubblydecentsidewinder" /><meta name="twitter:image" content="https://api.redgifs.com/v2/gifs/bubblydecentsidewinder/files/BubblyDecentSidewinder-large.jpg" /><meta name="twitter:image:width" content="2048" /><meta name="twitter:image:height" content="3078" /><script type="application/ld+json">{"@context":"http://schema.org","@type":"SocialMediaPosting","url":"https://www.redgifs.com/watch/bubblydecentsidewinder","headline":"Eva Angelina Fake Boobs Fake Tits Porn Image by useme4porn","keywords":"Eva Angelina,Fake Boobs,Fake Tits","mainEntityOfPage":true,"description":"Enjoy this Eva Angelina porn BubblyDecentSidewinder from anonymous. Sign up for free and start building your porn collection from the millions of GIFs and images free on RedGIFs","datePublished":"%2024-%01-%28UTC%20:%Jan:%th.0000","author":{"type":"Person","name":"anonymous","url":"https://www.redgifs.com/users/anonymous"},"interactionStatistic":{"@type":"InteractionCounter","interactionType":"http://schema.org/LikeAction","userInteractionCount":0},"image":{"@type":"ImageObject","author":"anonymous","contentUrl":"https://api.redgifs.com/v2/gifs/bubblydecentsidewinder/files/BubblyDecentSidewinder-large.jpg","creator":"anonymous","description":"Enjoy this Eva Angelina porn BubblyDecentSidewinder from anonymous. Sign up for free and start building your porn collection from the millions of GIFs and images free on RedGIFs","embedUrl":"https://www.redgifs.com/ifr/bubblydecentsidewinder","height":0,"keywords":"Eva Angelina,Fake Boobs,Fake Tits","name":"Eva Angelina Porn GIF","representativeOfPage":true,"thumbnailUrl":"https://api.redgifs.com/v2/gifs/bubblydecentsidewinder/files/BubblyDecentSidewinder-small.jpg","uploadDate":"%2024-%01-%28UTC%20:%Jan:%th.0000","url":"https://www.redgifs.com/watch/bubblydecentsidewinder","width":0,"interactionStatistic":{"@type":"InteractionCounter","interactionType":"http://schema.org/WatchAction","userInteractionCount":0}}}</script><script>var is_texan = false;</script></head><body><noscript>Enable JavaScript to access millions of porn GIFs and pics free on RedGIFs</noscript><div id="root"></div><div id="portal-root"></div><script>(function(){function c(){var b=a.contentDocument||a.contentWindow.document;if(b){var d=b.createElement('script');d.innerHTML="window.__CF$cv$params={r:'8c03c65a4ad9874c',t:'MTcyNTg0OTIyMC4wMDAwMDA='};var a=document.createElement('script');a.nonce='';a.src='/cdn-cgi/challenge-platform/scripts/jsd/main.js';document.getElementsByTagName('head')[0].appendChild(a);";b.getElementsByTagName('head')[0].appendChild(d)}}if(document.body){var a=document.createElement('iframe');a.height=1;a.width=1;a.style.position='absolute';a.style.top=0;a.style.left=0;a.style.border='none';a.style.visibility='hidden';document.body.appendChild(a);if('loading'!==document.readyState)c();else if(window.addEventListener)document.addEventListener('DOMContentLoaded',c);else{var e=document.onreadystatechange||function(){};document.onreadystatechange=function(b){e(b);'loading'!==document.readyState&&(document.onreadystatechange=e,c())}}}})();</script></body></html>""")
