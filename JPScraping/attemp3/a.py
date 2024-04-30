from bs4 import BeautifulSoup

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

      
      <footer>
        <div id="viewlet-below-content">



    <div class="visualClear"><!-- --></div>

    <div class="documentActions">
        

            <p class="hiddenStructure">Azioni sul documento</p>

            <ul>
                  <li id="document-action-print">
                      <a href="javascript:this.print();" title="">Stampa</a>
                  </li>
            </ul>
        

        

    </div>


<div class="documentByLine" id="plone-document-byline">
  <div class="documentByLineContent">
    <i class="far fa-calendar-alt"></i>
    

    
    <!--span class="documentPublished"
          tal:condition="published">
      <span i18n:translate="box_published" tal:condition="published_current_day">
        published
      </span>
      <span i18n:domain="design.plone.theme"
            i18n:translate="box_published_on"
            tal:condition="not:published_current_day">
        published on
      </span>
      <tal:comment condition="nothing"> format della data cambiato ticket #14437</tal:comment>
      <span class="pat-moment"
            tal:define="format python: published_current_day and 'relative' or 'calendar'"
            data-pat-moment="LLL"
            tal:content="published" />
      <tal:sep condition="modified">—</tal:sep>
    </span-->

    <span class="documentModified">
      <span>ultima modifica</span>
      
      <span class="pat-moment" data-pat-moment="format:LLL;">2022-09-30T14:57:53+02:00</span>
    </span>
    

    
  </div>
  
  
</div>







<div id="customer-satisfaction">
    <form action="https://agrea.regione.emilia-romagna.it/agenzia/agenzia/@customer-satisfaction-add" method="POST">
        <fieldset>
            <div style="display: none">
  <input type="text" value="" name="conferma_nome" />
</div>

            <div class="field">
                <legend>Questa pagina ti è stata utile?</legend>
                <div class="btn-group" role="radiogroup" aria-labelledby="cs-form-radiogroup-label">
                    <label class="plone-btn plone-btn-default feedback-label feedback-success" for="si">
                        <input type="radio" id="si" name="vote" value="ok" aria-controls="cs-collapsible-form-area" class="sr-only" />
                        <i aria-hidden="true" class="glyphicon glyphicon-thumbs-up"></i>
                        <span class="sr-only">Si</span>
                    </label>
                    <label class="plone-btn plone-btn-default feedback-label feedback-danger" for="no">
                        <input type="radio" id="no" name="vote" value="nok" aria-controls="cs-collapsible-form-area" class="sr-only" />
                        <i aria-hidden="true" class="glyphicon glyphicon-thumbs-down"></i>
                        <span class="sr-only">No</span>
                    </label>
                </div>
            </div>
            <div id="cs-collapsible-form-area" role="region" aria-expanded="false" aria-hidden="true" style="display: none;">
                <label for="rer-customersatisfaction-comment" class="sr-only">Spiegaci perché e aiutaci a migliorare la qualità del sito</label>
                <textarea title="Spiegaci perché e aiutaci a migliorare la qualità del sito" placeholder="Spiegaci perché e aiutaci a migliorare la qualità del sito" id="rer-customersatisfaction-comment" name="comment"></textarea>
                <button type="submit" class="plone-btn plone-btn-primary">Invia il tuo commento</button>
            </div>
        </fieldset>
    </form>
</div>
</div>
      </footer>
    </article><aside id="portal-column-two">
      
        
<div class="portletWrapper" id="portletwrapper-706c6f6e652e7269676874636f6c756d6e0a636f6e746578740a2f61677265612f6167656e7a69610a6e617669676174696f6e" data-portlethash="706c6f6e652e7269676874636f6c756d6e0a636f6e746578740a2f61677265612f6167656e7a69610a6e617669676174696f6e">
<aside class="portlet portletNavigationTree" role="navigation">

    <header class="portletHeader">
        <a href="https://agrea.regione.emilia-romagna.it/agenzia" class="tile">In questa sezione</a>
    </header>

    <nav class="portletContent lastItem">
        <ul class="navTree navTreeLevel0">
            
            



<li class="navTreeItem visualNoMarker navTreeFolderish section-attivita-e-funzioni">

    

        <a href="https://agrea.regione.emilia-romagna.it/agenzia/attivita-e-funzioni" title="" class="state-published navTreeFolderish ">

             

            

            Attività e funzioni
        </a>
        

    
</li>

<li class="navTreeItem visualNoMarker section-certificazione-iso-iec-27001">

    

        <a href="https://agrea.regione.emilia-romagna.it/agenzia/certificazione-iso-iec-27001" title="Lo standard ISO/IEC 27001:2013 che definisce i requisiti e le regole per impostare e gestire un Sistema di gestione della sicurezza delle informazioni (SGSI)" class="state-published ">

             

            

            Certificazione ISO/IEC 27001:2013
        </a>
        

    
</li>

<li class="navTreeItem visualNoMarker navTreeFolderish section-governance">

    

        <a href="https://agrea.regione.emilia-romagna.it/agenzia/governance" title="" class="state-published navTreeFolderish ">

             

            

            Governance
        </a>
        

    
</li>

<li class="navTreeItem visualNoMarker section-organigramma">

    

        <a href="https://agrea.regione.emilia-romagna.it/agenzia/organigramma" title="" class="state-published ">

             

            

            Organigramma di Agrea
        </a>
        

    
</li>

<li class="navTreeItem visualNoMarker navTreeFolderish section-sicurezza-delle-informazioni">

    

        <a href="https://agrea.regione.emilia-romagna.it/agenzia/sicurezza-delle-informazioni" title="" class="state-published navTreeFolderish ">

             

            

            Sicurezza delle Informazioni
        </a>
        

    
</li>

<li class="navTreeItem visualNoMarker section-struttura-e-persone">

    

        <a href="https://agrea.regione.emilia-romagna.it/amministrazione-trasparente/organizzazione/articolazione-degli-uffici-1" title="L’Agenzia si articola in una Direzione e due Servizi, ai quali si aggiunge uno staff di supporto alle attività del Direttore per la gestione delle attività di carattere trasversale. Sono organi dell’Agenzia il Direttore e il Revisore unico." class="state-published ">

             

            

            Struttura e persone
        </a>
        

    
</li>

<li class="navTreeItem visualNoMarker navTreeFolderish section-utilita">

    

        <a href="https://agrea.regione.emilia-romagna.it/agenzia/utilita" title="" class="state-published navTreeFolderish ">

             

            

            Utilità
        </a>
        

    
</li>




        </ul>
    </nav>
</aside>


</div>


      
    </aside></div>

    

    
    

    

    <div class="portlet rerPortletAdvancedStatic valuta-sito"><p><a href="contact-info" title="Valuta questo sito"><span class="valuta-sito-content"><span class="valuta-sito-text">Non hai trovato quello che cerchi?</span></span></a></p></div><footer id="portal-footer-wrapper">
      <div class="portal-footer">
    
<div class="portletWrapper" id="portletwrapper-706c6f6e652e666f6f746572706f72746c6574730a636f6e746578740a2f61677265610a76616c7574612d696e2d7369746f" data-portlethash="706c6f6e652e666f6f746572706f72746c6574730a636f6e746578740a2f61677265610a76616c7574612d696e2d7369746f">


</div>

<div class="portletWrapper" id="portletwrapper-706c6f6e652e666f6f746572706f72746c6574730a636f6e746578740a2f61677265610a636f6e74617474692d6167726561" data-portlethash="706c6f6e652e666f6f746572706f72746c6574730a636f6e746578740a2f61677265610a636f6e74617474692d6167726561">

<section class="portlet rerPortletAdvancedStatic">
    <div class="portletHeader">
        <span class="headerImg" style="background-image:url()">
        </span>

        <h4 class="portlet-header">
            Contatti Agrea
        </h4>

    </div>

    <section class="portletContent">
        <div class="colonna-1-di-3">
<h4>Agenzia regionale per le erogazioni in agricoltura</h4>
<p>Largo Caduti del Lavoro 6,<br /> 40122 Bologna</p>
<p><a href="https://agrea.regione.emilia-romagna.it/amministrazione-trasparente/organizzazione/telefono-e-posta-elettronica">Cerca telefoni e indirizzi</a></p>
<p><strong>URP AGREA</strong><br /><a href="mailto:agreaurp@regione.emilia-romagna.it">agreaurp@regione.emilia-romagna.it</a></p>
</div>
<div class="colonna-1-di-3">
<h3>Redazione</h3>
<hr />
<ul>
<li><a href="https://agrea.regione.emilia-romagna.it/info">Informazioni sul sito e crediti</a></li>
<li><strong>Scrivici</strong>: <a href="mailto:agrearedazione@regione.emilia-romagna.it">e-mail</a></li>
</ul>
</div>
<div class="colonna-1-di-3">
<h3>Trasparenza</h3>
<hr />
<ul>
<li><a href="https://agrea.regione.emilia-romagna.it/amministrazione-trasparente">Amministrazione trasparente</a></li>
<li><a href="https://trasparenza.regione.emilia-romagna.it/altri-contenuti/anticorruzione/segnala-irregolarita-o-illeciti">Segnala illeciti o irregolarità</a></li>
<li><a href="https://agrea.regione.emilia-romagna.it/note-legali">Note legali e copyright</a></li>
<li><a href="https://agrea.regione.emilia-romagna.it/privacy">Privacy e cookie</a></li>
<li><a data-cc-open-settings="" href="#">Gestisci i cookie</a></li>
<li><a href="https://agrea.regione.emilia-romagna.it/accessibilita">Dichiarazione di accessibilità</a></li>
</ul>
</div>
    </section>

    
</section>
</div>

<div class="portletWrapper" id="portletwrapper-706c6f6e652e666f6f746572706f72746c6574730a636f6e746578740a2f61677265610a636f6c6f70686f6e2d6167726561" data-portlethash="706c6f6e652e666f6f746572706f72746c6574730a636f6e746578740a2f61677265610a636f6c6f70686f6e2d6167726561">

<section class="portlet rerPortletAdvancedStatic footer-actions">
    <div class="portletHeader">
        <span class="headerImg" style="background-image:url()">
        </span>

        <h4 class="portlet-header">
            Colophon Agrea
        </h4>

    </div>

    <section class="portletContent">
        <div class="tinyAlignCenter">C.F. 912 150 603 76</div>
<div class="tinyAlignCenter">email <a href="mailto:agrea@regione.emilia-romagna.it">agrea@regione.emilia-romagna.it</a>, PEC <a href="mailto:agrea@postacert.regione.emilia-romagna.it">agrea@postacert.regione.emilia-romagna.it</a></div>
    </section>

    
</section>
</div>

<div class="portletWrapper" id="portletwrapper-706c6f6e652e666f6f746572706f72746c6574730a636f6e746578740a2f61677265610a6c6f676f2d726572" data-portlethash="706c6f6e652e666f6f746572706f72746c6574730a636f6e746578740a2f61677265610a6c6f676f2d726572">

<section class="portlet rerPortletAdvancedStatic footer-actions">
    <div class="portletHeader">
        <span class="headerImg" style="background-image:url()">
        </span>

        <h4 class="portlet-header">
            Logo RER
        </h4>

    </div>

    <section class="portletContent">
        <hr />
<p><img alt="Logo Regione Emilia-Romagna" class="image-inline" src="https://agrea.regione.emilia-romagna.it/impostazioni/immagini/logo-regione.png/@@images/5fd151d5-14a7-471d-b218-98e596f6d07a.png" title="Logo Regione Emilia-Romagna" /></p>
    </section>

    
</section>
</div>

<div class="portletWrapper" id="portletwrapper-706c6f6e652e666f6f746572706f72746c6574730a636f6e746578740a2f61677265610a636f6e74617474692d726572" data-portlethash="706c6f6e652e666f6f746572706f72746c6574730a636f6e746578740a2f61677265610a636f6e74617474692d726572">

<section class="portlet rerPortletAdvancedStatic">
    <div class="portletHeader">
        <span class="headerImg" style="background-image:url()">
        </span>

        <h4 class="portlet-header">
            Contatti rer
        </h4>

    </div>

    <section class="portletContent">
        <div class="colonna-1-di-2">
<h3>Recapiti</h3>
<p><strong>Regione Emilia-Romagna</strong><br />Viale Aldo Moro, 52<strong><br /></strong>40127 Bologna<br /><strong>Centralino</strong> <a href="tel:+39.0515271">051 5271</a><br /><a class="external-link" href="http://wwwservizi.regione.emilia-romagna.it/Cercaregione/Default.aspx?cons=0">Cerca telefoni o indirizzi</a></p>
</div>
<div class="colonna-1-di-2">
<h3><acronym title="Ufficio relazioni con il pubblico">URP</acronym></h3>
<p><strong>Sito web</strong>: <a href="http://www.regione.emilia-romagna.it/urp">www.regione.emilia-romagna.it/urp</a><br /> <strong>Numero verde: </strong><a href="tel:+39.800662200">800.66.22.00<br /></a><strong>Scrivici</strong>: <a href="mailto:urp@regione.emilia-romagna.it">e-mail</a> - <a href="mailto:urp@postacert.regione.emilia-romagna.it">PEC<br /></a></p>
</div>
    </section>

    
</section>
</div>

<div class="portletWrapper" id="portletwrapper-706c6f6e652e666f6f746572706f72746c6574730a636f6e746578740a2f61677265610a636f6c6f70686f6e" data-portlethash="706c6f6e652e666f6f746572706f72746c6574730a636f6e746578740a2f61677265610a636f6c6f70686f6e">

<section class="portlet rerPortletAdvancedStatic footer-actions">
    <div class="portletHeader">
        <span class="headerImg" style="background-image:url()">
        </span>

        <h4 class="portlet-header">
            Colophon
        </h4>

    </div>

    <section class="portletContent">
        <div class="tinyAlignCenter">C.F. 800 625 903 79</div>
    </section>

    
</section>
</div>


</div>

<!-- Piwik Prod New Tracking Code -->
<script type="text/javascript">
    var _paq = _paq || [];
var index1 = location.href.indexOf("applicazioni.regione.emilia-romagna.it");
var index2 = location.href.indexOf("applicazionitest.regione.emilia-romagna.it");
var index3 = location.href.indexOf("cm.regione.emilia-romagna.it");
var index4 = location.href.indexOf("test-www.regione.emilia-romagna.it");
var index5 = location.href.indexOf("test-cm.regione.emilia-romagna.it");
var index6 = location.href.indexOf("localhost");
var index7 = location.href.indexOf("//10.");
(function(){ var u="https://statisticheweb.regione.emilia-romagna.it/analytics/";
if (index1==-1 && index2==-1 && index3==-1 && index4==-1 && index5==-1 && index6==-1 && index7==-1){
    _paq.push(['setSiteId', 59]);
    _paq.push(['setTrackerUrl', u+'piwik.php']);
    _paq.push(['setDocumentTitle', document.domain + "/" + document.title]);
    _paq.push(['trackPageView']);
    _paq.push(['enableLinkTracking']);
    var d=document, g=d.createElement('script'), s=d.getElementsByTagName('script')[0]; g.type='text/javascript'; g.defer=true; g.async=true; g.src=u+'piwik.js';
    s.parentNode.insertBefore(g,s); }})();
</script>
<noscript><p><img src="https://statisticheweb.regione.emilia-romagna.it/analytics/piwik.php?idsite=59" style="border:0" alt="" /></p></noscript>
<!-- End Piwik Prod New Tracking Code -->
    </footer><a href="javascript:" aria-hidden="true" id="return-to-top" title="Return to top" style="display: none"><i class="fas fa-chevron-up"></i></a>

  </body>
</html>

"""

soup = BeautifulSoup(html_content, 'html.parser')

# Remove script and style elements
for script in soup(["script", "style"]):
    script.decompose()

# Get the text
text = soup.get_text()

# Break into lines and remove leading and trailing space on each
lines = (line.strip() for line in text.splitlines())
# Break multi-headlines into a line each
chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
# Drop blank lines
text = '\n'.join(chunk for chunk in chunks if chunk)

print(text)