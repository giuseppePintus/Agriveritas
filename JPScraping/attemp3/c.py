from bs4 import BeautifulSoup
import re
import urllib.parse

html_content = """
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="it" xml:lang="it">
  <head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /><link rel="stylesheet" href="https://agrea.regione.emilia-romagna.it/++resource++redturtle.chefcookie/styles.css?v=2.1.0" /><link rel="canonical" href="https://agrea.regione.emilia-romagna.it/agenzia" /><link rel="search" href="https://agrea.regione.emilia-romagna.it/@@search" title="Cerca nel sito" /><link rel="stylesheet" type="text/css" href="https://agrea.regione.emilia-romagna.it/++plone++production/++unique++2022-12-22T16:36:52.714276/default.css" data-bundle="production" /><link rel="stylesheet" type="text/css" href="https://agrea.regione.emilia-romagna.it/++plone++static/++unique++2019-05-30%2009%3A59%3A06.112978/plone-compiled.css" data-bundle="plone" /><link rel="stylesheet" type="text/css" href="https://agrea.regione.emilia-romagna.it/++plone++rer.parer.policy/++unique++2022-12-22%2016%3A36%3A52.713396/stylesheets/rerparerpolicy.css" data-bundle="rer-parer-policy-bundle" /><link rel="stylesheet" type="text/css" href="https://agrea.regione.emilia-romagna.it/++resource++redturtle.tiles.management/tiles-management-compiled.css?version=2023-06-21%2015%3A47%3A54.905528" data-bundle="redturtle-tiles-management" /><link rel="stylesheet" type="text/css" href="https://agrea.regione.emilia-romagna.it/++theme++rer.agidtheme.base/css/rer-agidtheme-base-bundle.css?version=2023-11-27%2015%3A07%3A15.786309" data-bundle="rer-agidtheme-base-css-bundle" /><link rel="stylesheet" type="text/css" href="https://agrea.regione.emilia-romagna.it/++plone++rer.solrpush/++unique++2023-11-27%2015%3A06%3A45.538580/styles.css" data-bundle="rer-solrpush-css-bundle" /><link rel="stylesheet" type="text/css" href="https://agrea.regione.emilia-romagna.it/++plone++redturtle-patterns-slider/++unique++2017-09-18%2014%3A23%3A45.288718/build/redturtle-patterns-slider-bundle-compiled.min.css" data-bundle="redturtle-patterns-slider-bundle" /><link rel="stylesheet" type="text/css" href="https://agrea.regione.emilia-romagna.it/++plone++rer.customersatisfaction/++unique++2023-06-21%2015%3A47%3A47.469343/rer-customersatisfaction.css" data-bundle="rer-customer-satisfaction" /><link rel="stylesheet" type="text/css" href="https://agrea.regione.emilia-romagna.it/++resource++wildcard-media/components/mediaelement/build/mediaelementplayer.min.css?version=2018-03-15%2015%3A33%3A44.714085" data-bundle="wildcard-media" /><script type="text/javascript" src="https://agrea.regione.emilia-romagna.it/++resource++redturtle.chefcookie/chefcookie/chefcookie.min.js?v=2.1.0"></script><script type="text/javascript" src="https://agrea.regione.emilia-romagna.it/++resource++redturtle.chefcookie/redturtle_chefcookie.js?v=2.1.0"></script><script type="text/javascript" src="https://agrea.regione.emilia-romagna.it/cookie_config.js?v=2.1.0_cc_1_"></script><script type="text/javascript">PORTAL_URL = 'https://agrea.regione.emilia-romagna.it';</script><script type="text/javascript" src="https://agrea.regione.emilia-romagna.it/++plone++production/++unique++2022-12-22T16:36:52.714276/default.js" data-bundle="production"></script><script type="text/javascript" src="https://agrea.regione.emilia-romagna.it/++plone++static/++unique++2019-05-30%2009%3A59%3A06.112978/plone-compiled.min.js" data-bundle="plone"></script><script type="text/javascript" src="https://agrea.regione.emilia-romagna.it/++resource++redturtle.tiles.management/tiles-management-compiled.js?version=2023-06-21%2015%3A47%3A54.905528" data-bundle="redturtle-tiles-management"></script><script type="text/javascript" src="https://agrea.regione.emilia-romagna.it/++theme++rer.agidtheme.base/js/dist/rer-agidtheme-base-bundle-compiled.min.js?version=2023-11-27%2015%3A07%3A15.831310" data-bundle="rer-agidtheme-base-js-bundle"></script><script type="text/javascript" src="https://agrea.regione.emilia-romagna.it/++theme++design.plone.theme/js/dist/design-plone-theme-bundle-compiled.min.js?version=2022-08-16%2015%3A20%3A20.185344" data-bundle="design-plone-theme-js-bundle"></script><script type="text/javascript" src="https://agrea.regione.emilia-romagna.it/++plone++rer.immersivereader/++unique++2022-01-20%2015%3A34%3A34.137289/js/dist/rer-immersive-reader-compiled.min.js" data-bundle="rer-immersive-reader-bundle"></script><script type="text/javascript" src="https://agrea.regione.emilia-romagna.it/++plone++rer.agidtheme.base/++unique++2023-11-27%2015%3A07%3A15.763309/chefcookie_modal.js" data-bundle="rer-chefcookie-modal-bundle"></script><script type="text/javascript" src="https://agrea.regione.emilia-romagna.it/++theme++rer.agidtheme.base/js/dist/rer-agidtheme-base-icons-bundle.min.js?version=2023-11-27%2015%3A07%3A15.861311" data-bundle="rer-agidtheme-base-icons-bundle"></script><script type="text/javascript" src="https://agrea.regione.emilia-romagna.it/++plone++redturtle-patterns-slider/++unique++2017-09-18%2014%3A23%3A45.288718/build/redturtle-patterns-slider-bundle-compiled.js" data-bundle="redturtle-patterns-slider-bundle"></script><script type="text/javascript" src="https://agrea.regione.emilia-romagna.it/++plone++rer.customersatisfaction/++unique++2023-06-21%2015%3A47%3A47.469343/rer-customersatisfaction.js" data-bundle="rer-customer-satisfaction"></script><script type="text/javascript" src="https://agrea.regione.emilia-romagna.it/++plone++rer.agidtheme.base/++unique++2023-11-27%2015%3A07%3A15.766309/widget-v2.js" data-bundle="rer-climate-clock-widget-bundle"></script><script type="text/javascript" src="https://agrea.regione.emilia-romagna.it/++resource++wildcard-media/integration.js?version=2018-03-15%2015%3A33%3A44.714085" data-bundle="wildcard-media"></script>
    <title>L'agenzia — Agenzia regionale per le — erogazioni in agricoltura</title>

    <link rel="apple-touch-icon" href="/++theme++rer.agidtheme.base/apple-touch-icon.png" />
    <link rel="apple-touch-icon-precomposed" sizes="144x144" href="/++theme++rer.agidtheme.base/apple-touch-icon-144x144-precomposed.png" />
    <link rel="apple-touch-icon-precomposed" sizes="114x114" href="/++theme++rer.agidtheme.base/apple-touch-icon-114x114-precomposed.png" />
    <link rel="apple-touch-icon-precomposed" sizes="72x72" href="/++theme++rer.agidtheme.base/apple-touch-icon-72x72-precomposed.png" />
    <link rel="apple-touch-icon-precomposed" sizes="57x57" href="/++theme++rer.agidtheme.base/apple-touch-icon-57x57-precomposed.png" />
    <link rel="apple-touch-icon-precomposed" href="/++theme++rer.agidtheme.base/apple-touch-icon-precomposed.png" />

    <link href="/++theme++rer.agidtheme.base/++theme++design.plone.theme/css/fonts.css" rel="stylesheet" />

  <meta name="viewport" content="width=device-width, initial-scale=1.0" /><meta content="summary" name="twitter:card" /><meta content="Agenzia regionale per le &amp;mdash; erogazioni in agricoltura" property="og:site_name" /><meta content="L'agenzia" property="og:title" /><meta content="website" property="og:type" /><meta content="" property="og:description" /><meta content="https://agrea.regione.emilia-romagna.it/agenzia" property="og:url" /><meta content="https://agrea.regione.emilia-romagna.it/@@site-logo/logo-agrea-100.png" property="og:image" /><meta content="image/png" property="og:image:type" /><meta name="generator" content="Plone - http://plone.com" />
        <link rel="shortcut icon" type="image/x-icon" href="https://agrea.regione.emilia-romagna.it/favicon.ico" />
    </head>
  <body id="visual-portal-wrapper" class="customer-satisfaction-enabled frontend icons-on portaltype-document section-agenzia site-agrea subsection-agenzia template-tiles_view thumbs-on userrole-anonymous viewpermission-view" dir="ltr" data-i18ncatalogurl="https://agrea.regione.emilia-romagna.it/plonejsi18n" data-view-url="https://agrea.regione.emilia-romagna.it/agenzia/agenzia" data-pat-plone-modal="{&quot;actionOptions&quot;: {&quot;displayInModal&quot;: false}}" data-portal-url="https://agrea.regione.emilia-romagna.it" data-pat-pickadate="{&quot;date&quot;: {&quot;selectYears&quot;: 200}, &quot;time&quot;: {&quot;interval&quot;: 5 } }" data-base-url="https://agrea.regione.emilia-romagna.it/agenzia/agenzia">

    


    <header id="portal-top">
      <div class="skip-link-wrapper">
    <a accesskey="2" class="skip-link skip-link-content" href="#content">Vai al Contenuto</a>
    <a accesskey="6" class="skip-link skip-link-navigation" href="#portal-mainnavigation">Vai alla navigazione del sito</a>
</div>

<div id="header-banner">
    <div class="header-banner-inner">
        <div class="header-banner-owner">
          <a href="https://www.regione.emilia-romagna.it/">Regione Emilia-Romagna</a>
        </div>
        
        
        
    </div>
</div>

<div id="portal-header"><a id="portal-logo" title="Home" href="https://agrea.regione.emilia-romagna.it">
    <img src="https://agrea.regione.emilia-romagna.it/@@site-logo/logo-agrea-100.png" alt="" />
    
    
        <div class="site-subtitle subtitle-normal">
            <span>Agenzia regionale per le</span>
            <span class="subtitle">erogazioni in agricoltura</span>
        </div>
    
</a><div class="search-social-wrapper no-social-links"><div id="portal-searchbox">

    <form id="searchGadget_form" action="https://agrea.regione.emilia-romagna.it/@@search" role="search" data-pat-livesearch="ajaxUrl:https://agrea.regione.emilia-romagna.it/@@ajax-search" class="">

        <div class="LSBox">
          <label class="hiddenStructure" for="searchGadget">Cerca nel sito</label>

          <input name="SearchableText" type="text" size="18" id="searchGadget" title="Cerca nel sito" placeholder="Cerca nel sito" class="searchField" />

          <button class="search-button" type="submit" aria-label="Cerca" title="Cerca">
          </button>

        </div>
    </form>

</div><button id="search-toggle" aria-controls="portal-searchbox" aria-label="Apri/chiudi ricerca" title="Apri/chiudi ricerca"><i class="fas fa-search"></i><span class="close-icon"></span><span class="sr-only">SEARCH</span></button><div class="plone-navbar-header"><button type="button" class="plone-navbar-toggle" aria-controls="portal-mainnavigation" aria-expanded="false"><span class="sr-only">Toggle navigation</span><i class="fas fa-bars"></i></button></div></div></div>

    </header>

    <div id="portal-mainnavigation">
  <nav aria-label="Sezioni" class="globalnavWrapper">
    <div class="globalnavClose">
      <button id="globalnav-close" aria-controls="menu" aria-label="Esci dalla navigazione" title="Esci dalla navigazione">
          <span class="icon" aria-hidden="true"></span>
          <span class="sr-only">chiudi</span>
      </button>
    </div>
    <ul role="menubar" id="portal-globalnav">
      
        <li id="portaltab-0" class="plain">
          <a href="https://agrea.regione.emilia-romagna.it/agenzia" data-tabid="0" class="menuTabLink clickandgo"><span>L’agenzia</span></a>
        </li>
      
        <li id="portaltab-1" class="plain">
          <a href="https://agrea.regione.emilia-romagna.it/come-fare-per" data-tabid="1" class="menuTabLink clickandgo"><span>Come fare per</span></a>
        </li>
      
        <li id="portaltab-2" class="plain">
          <a href="https://agrea.regione.emilia-romagna.it/settori-di-intervento" data-tabid="2" class="menuTabLink clickandgo"><span>Settori di intervento</span></a>
        </li>
      
        <li id="portaltab-3" class="plain">
          <a href="#" data-tabid="3" class="menuTabLink " aria-haspopup="true" aria-expanded="false" role="menuitem"><span>Servizi online</span></a>
        </li>
      
    </ul>
  </nav>

</div>

    <aside id="global_statusmessage">
      

      <div>
      </div>
    </aside>

    <div id="viewlet-above-content"><nav id="portal-breadcrumbs" class="plone-breadcrumb">
  <div class="container">
    <span id="breadcrumbs-you-are-here" class="hiddenStructure">Tu sei qui:</span>
    <ol aria-labelledby="breadcrumbs-you-are-here">
      <li id="breadcrumbs-home">
        <a title="Home" href="https://agrea.regione.emilia-romagna.it">
          Home
        </a>
      </li>
      
    </ol>
  </div>
</nav>

<div class="share">
    

    <div class="share-slider">
        <div class="share-title">
            <a href="#" class="share-toggle">
                <span class="share-text">Condividi</span>
            </a>
        </div>
        <div class="share-options">
            <ul class="social-list">
                <li><a title="Facebook - apri in una nuova scheda" href="https://www.facebook.com/sharer/sharer.php?u=https://agrea.regione.emilia-romagna.it/agenzia/agenzia" target="_blank"><i class="fab fa-facebook-f"></i><span class="u-hiddenVisually">Facebook</span></a></li><li><a title="Twitter - apri in una nuova scheda" href="https://twitter.com/intent/tweet?url=https://agrea.regione.emilia-romagna.it/agenzia/agenzia&amp;text=L%27agenzia" target="_blank"><i class="fab fa-twitter"></i><span class="u-hiddenVisually">Twitter</span></a></li><li><a title="Linkedin - apri in una nuova scheda" href="http://www.linkedin.com/shareArticle?url=https://agrea.regione.emilia-romagna.it/agenzia/agenzia&amp;title=L%27agenzia" target="_blank"><i class="fab fa-linkedin-in"></i><span class="u-hiddenVisually">Linkedin</span></a></li>
            </ul>
        </div>
    </div>
    <div class="share-button">
        <a href="#" class="share-toggle">
            <span class="share-icon"></span>
            <span class="sr-only">Attiva condividi</span>
        </a>
    </div>
</div>

</div>

    <div id="column-wrapper" class="with-column-two"><article id="portal-column-content">

      

      <div>


        

        <article id="content">

          

          <header>
            <div id="viewlet-above-content-title"><span id="social-tags-body" style="display: none" itemscope="" itemtype="http://schema.org/WebPage">
  <span itemprop="name">L'agenzia</span>
  <span itemprop="description"></span>
  <span itemprop="url">https://agrea.regione.emilia-romagna.it/agenzia</span>
  <span itemprop="image">https://agrea.regione.emilia-romagna.it/@@site-logo/logo-agrea-100.png</span>
</span>
</div>
            
                <h1 class="documentFirstHeading">L'agenzia</h1>
            
            <div id="viewlet-below-content-title"></div>

            
                
            
          </header>

          <div id="viewlet-above-content-body">

</div>
          <div id="content-core">
            
      
        
        
          <div class="tiles-management ">
  <div class="tilesWrapper">
    
    <div class="tilesList">
      
        <div class="tileWrapper " data-tileid="" data-tiletype="" data-tilehidden="" data-token="">
          
          
    <div class="tile tile-advanced-static senza-titolo">
        <div class="tile-container">
        <!-- HEADER -->
        <h2 class="tileTitle">
            
            
                <span class="ast_title">Agenzia</span>
            
        </h2>
        <!-- BODY -->
        <div class="tile-text tileBody"><p>Agrea è l’Organismo pagatore regionale (Opr) che eroga gli aiuti, i premi e i contributi all’insieme degli <strong>operatori del settore agricolo</strong> previsti dalle disposizioni comunitarie, nazionali e regionali.</p>
<p>L’Agenzia è stata istituita dalla Regione Emilia-Romagna con la <a href="https://demetra.regione.emilia-romagna.it/al/articolo?urn=er:assemblealegislativa:legge:2001;21" rel="noopener noreferrer" target="_blank">Legge regionale n. 21 del 23 luglio 2001</a> ed è stata riconosciuta dal Ministero delle Politiche agricole, alimentari, forestali e del turismo a più riprese <strong>dal 2002 al 2008</strong> per l’acquisizione graduale delle competenze sui settori di intervento, per operare con le funzioni di Organismo pagatore per gli aiuti finanziari a carico del <strong>Fondo europeo agricolo di garanzia</strong> (Feaga) e del <strong>Fondo europeo agricolo di sviluppo rurale</strong> (Feasr).</p>
<p>L’Agenzia è dotata di <strong>autonomia amministrativa, organizzativa e contabile</strong>; le risorse finanziarie, necessarie per il funzionamento, provengono dalla Regione che le eroga annualmente. Agrea può ricevere contributi proventi da altri soggetti, purché rientranti nella sfera pubblica.</p>
<p></p></div>
        <!-- FOOTER -->
        
        </div>
    </div>

        </div>
      
    </div>
  </div>

</div>
        
        
      
    
          </div>
          <div id="viewlet-below-content-body"></div>

          
        </article>

        


      </div>

      
  </body>
</html>
"""

soup = BeautifulSoup(html_content, 'html.parser')

# Extract title
title = soup.find('title').text.strip()

# Extract URL source
url_source = urllib.parse.urljoin('https://agrea.regione.emilia-romagna.it', soup.find('link', rel='canonical')['href'])

# Extract markdown content
markdown_content = ''
for p in soup.find_all('p'):
    text = re.sub(r'\s+', ' ', p.text.strip())
    markdown_content += f'{text}\n\n'

output = f"""Title: {title}

URL Source: {url_source}

Markdown Content:
{markdown_content}"""

print(output)