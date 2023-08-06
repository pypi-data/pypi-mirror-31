<p align="center">
  <img src="https://github.com/jamesssooi/fonty/raw/master/artwork/logo.png" alt="Logo of fonty">
</p>

<h3 align="center">A command-line tool to download, manage and convert fonts</h3>

<p align="center">
  <img src="https://raw.githubusercontent.com/jamesssooi/fonty/master/artwork/hero.png" alt="Screenshot of fonty commands">
</p>

**fonty** is a command line interface that helps you simplify your font management workflow by allowing you to install and uninstall fonts like a package manager (think npm, apt-get, chocolatey). It can also help you create webfonts and generate @font-face declarations so that you can focus on building great websites.
## Table of Contents
* [Installation](#1--installation)
* [Basic Usage](#2--basic-usage)
    * [Installing and uninstalling fonts](#21--installing-and-uninstalling-fonts)
    * [Listing installed fonts](#22--listing-installed-fonts)
    * [Generating webfonts](#23--generating-webfonts)
    * [Managing font sources](#24--managing-font-sources)
* [Commands](#3--commands)
    * [`fonty install`](#31--fonty-install)
    * [`fonty uninstall`](#32--fonty-uninstall)
    * [`fonty list`](#33--fonty-list)
    * [`fonty webfont`](#34--fonty-webfont)
    * [`fonty source`](#35--fonty-source)
* [Font Sources](#4--font-sources)
    * [Default sources](#41--default-sources)
    * [Hosting your own](#42--hosting-your-own)
* [Roadmap](#5--roadmap)
* [Licensing](#6--licensing)

## 1 &nbsp;&nbsp; Installation
*__Prerequisites__: Please make sure you have at least [Python 3](https://www.python.org/downloads/) installed*

```bash
> pip install fonty
```

**fonty** is only available for macOS and Windows for now. Linux support is planned.

## 2 &nbsp;&nbsp; Basic Usage
Append any command with `--help` for a detailed help text of what you can do.
```bash
> fonty [command] --help
```

### 2.1 &nbsp;&nbsp; Installing and uninstalling fonts
#### 2.1.1 &nbsp;&nbsp; Installing fonts
Downloading and installing a font from [subscribed sources](#4--font-sources):
```bash
> fonty install Lato
```

Downloading a font into a directory:
```bash
> fonty install Lato -o "~/Desktop/Lato"
```

Download only the bold and bold italic variants of a font:
```bash
> fonty install Lato -v 700,700i
```

*__Further reading__: [`fonty install`](#31--fonty-install)*

---

#### 2.1.2 &nbsp;&nbsp; Uninstalling fonts
Uninstalling a font family from your computer:
```bash
> fonty uninstall Lato
```

Uninstalling only a specific variant:
```bash
# This only removes the 900i (Black Italic) variant of the font
> fonty uninstall Lato -v 900i
```

*__Further reading__: [`fonty uninstall`](#32--fonty-uninstall)*

---

### 2.2 &nbsp;&nbsp; Listing installed fonts
List all installed fonts
```bash
> fonty list
```

List further details about a specific installed font
```bash
> fonty list Lato
```

*__Further reading__: [`fonty list`](#33--fonty-list)*

---

### 2.3 &nbsp;&nbsp; Generating webfonts
**fonty** can help you convert fonts to `woff` and `woff2` formats, which is supported by all major browsers (IE9 and above) as well as generate their `@font-face` declarations.

Convert all *.ttf fonts in this directory to webfonts:
```bash
> fonty webfont *.ttf
```

Generate webfonts into a specific directory:
```bash
> fonty webfont *.ttf -o ./webfonts
```

Download a font from your [subscribed sources](#4--font-sources) and convert:
```bash
> fonty webfont --download Lato
```

Convert an existing installed font on your computer:
```bash
> fonty webfont --installed Lato
```

*__Further reading__: [`fonty webfont`](#34--fonty-webfont)*

---

### 2.4 &nbsp;&nbsp; Managing font sources
**fonty** searches and downloads fonts from your list of subscribed sources. Upon installation, fonty automatically subscribes to a few [default sources](#41--default-sources). Here's how you can manage your subscriptions:

Adding a new font source:
```bash
> fonty source add http://url/to/source.json
```

Removing a font source:
```bash
# Deleting by URL
> fonty source remove http://url/to/source.json

# Deleting by ID
> fonty source remove e0f9cbd9977479825e1cd38aafb1660d
```

Show list of subscribed sources:
```bash
> fonty source list
```

Updating sources:
```bash
> fonty source update
```

*__Further reading__: [`fonty source`](#35--fonty-source), [Font Sources](#4--font-sources)*

---

## 3 &nbsp;&nbsp; Commands

#### 3.1 &nbsp;&nbsp; `fonty install`
```bash
> fonty install <FONT NAME> [OPTIONS]
# Example: `fonty install Lato`

> fonty install <FONT URL> [OPTIONS]
# Example: `fonty install http://url/to/Lato.ttf`

> fonty install --files <FONT FILES> [OPTIONS]
# Example: `fonty install --files *.ttf`
```
**Installs a font into the computer or into a directory.**

In it's default behaviour, **fonty** searches through your [subscribed sources](#4--font-sources) to download and install the specified font automatically. Alternatively, it can also support downloading `.ttf`/`.otf` files directly, or if a `--files` flag is passed, **fonty** can help you install local font files on your computer.

##### Options

* **`-v`/`--variants`** `text`
    * A comma separated list of variants with no spaces in between.
* **`-o`/`--output`** `path`
    * Output fonts into this directory. If supplied, the fonts won't be installed into the system.
* **`--files`** `flag`
    * If provided, read arguments as a list of font files to be installed. Files can be a glob pattern.

---

#### 3.2 &nbsp;&nbsp; `fonty uninstall`
```bash
> fonty uninstall <FONT NAME> [OPTIONS]
```

**Uninstalls a font from this computer.**

This command uninstalls the specified font from the computer and deletes them into the Trash or Recycle Bin.

##### Options

* **`-v`/`--variants`** `text`
    * A list of comma separated values of font variants with no spaces in between.

---

#### 3.3 &nbsp;&nbsp; `fonty list`
```bash
> fonty list [OPTIONS]
> fonty list <FONT NAME> [OPTIONS]
```

**Show a list of installed fonts**.

This command shows a list of all installed fonts in this computer, scanned through the user's font directory.

If a specific font name is specified, then this command prints a list of all the font files of that particular family.

##### Options

* **`--rebuild`** `flag`
    * If provided, rebuild the font manifest file.

---

#### 3.4 &nbsp;&nbsp; `fonty webfont`
```bash
> fonty webfont <FONT FILES> [OPTIONS]
> fonty webfont --download <FONT NAME> [OPTIONS]
> fonty webfont --installed <FONT NAME> [OPTIONS]
```

**Convert fonts to webfonts and generate @font-face declarations**.

This command convert fonts to `.woff` and `.woff2` formats, as well as generate their @font-face CSS declaration into a file named `styles.css`.

**fonty's** default behaviour is to convert a list of font files that you have provided. You can specify glob patterns for your file paths. Alternatively, it can also download fonts using the `--download` flag, or use an existing installed font on your computer using the `--installed` flag.

The [Web Open Font Format (WOFF)](https://developer.mozilla.org/en-US/docs/Web/Guide/WOFF) is a widely supported font format for web browsers, and should be sufficient for a large majority of use cases. You can read the compatibility tables on [caniuse.com](https://caniuse.com/#search=woff).

##### Options

* **`--download`** `flag`
    * If provided, download font from subscribed sources and convert.

* **`--installed`** `flag`
    * If provided, convert an existing font installed on the system.

* **`-o`/`--output`** `path`
    * Output webfonts into a specific directory.

---

#### 3.5 &nbsp;&nbsp; `fonty source`
```bash
> fonty source add <SOURCE URL>
```
**Adds a new font source.**

This command allows you to add and subscribe to a new font source. This allows you to have instant access to all of the source's fonts through the `fonty install` command.

---

```bash
> fonty source remove <SOURCE ID or SOURCE URL>
```

**Removes a subscribed font source.**

---

```bash
> fonty source list
```

**Print a list of subscribed font sources.**

This command shows a list of all subscribed sources, along with their IDs, update status, and number of available fonts.

---

```bash
> fonty source update [OPTIONS]
```

**Check all subscribed sources for available updates.**

When font sources are subscribed to, a local copy of the source is downloaded into your computer. Running this command updates your local copy with the latest one.

* **`f`/`--force`** `flag`
    * If provided, force all sources to be redownloaded and rebuild the search index.


## 4 &nbsp;&nbsp; Font Sources

**fonty** relies on font sources to resolve, download and install fonts. A font source is simply a JSON file containing an index of its fonts, and where to download them.

With **fonty**, you can subscribe to multiple font sources at the same time to have instant access to a wide variety of fonts through the `fonty install` command.

### 4.1 &nbsp;&nbsp; Default sources

Right out of the box, **fonty** is automatically subscribed to a few default font sources so you can enjoy the benefits of using **fonty** rightaway. These default sources are:

1. **fonty's Google Fonts Repository**
    * The entire [Google Fonts](https://fonts.google.com) repository, in a format that **fonty** understands.
    * **URL:** https://sources.fonty.io/googlefonts

2. **fonty's Open Source Fonts Repository**
    * A self-maintained list of open source fonts across the web.
    * **URL**: https://sources.fonty.io/fontyfonts

You can unsubscribe and subscribe from these sources at anytime. See the [`fonty source`](#35--fonty-source) command.

### 4.2 &nbsp;&nbsp; Hosting your own

You may wish to host your own repository for your personal usage, or perhaps you might want to make a set of fonts available for your entire team. A repository of fonts is a powerful concept that allows people to share and use fonts effortlessly.

While **fonty** is still in alpha, the schema and specifications for font sources is still largely a work in progress. As such until **fonty** is fully released, it is not encouraged for you to host your own font sources yet as the schema might go through a large amount of changes before it is finalised.

## 5 &nbsp;&nbsp; Roadmap
- [ ] Implement command to disable/enable fonts
- [ ] Finalise fonty sources schema and specifications
- [ ] Add support for installation via `homebrew`

## 6 &nbsp;&nbsp; Licensing
**fonty** is released under the [Apache License, Version 2.0](https://github.com/jamesssooi/fonty/blob/master/LICENSE).  

Copyright © 2018 [James] Ooi Weng Teik.

---
[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/images/badges/60-percent-of-the-time-works-every-time.svg)](https://forthebadge.com)
