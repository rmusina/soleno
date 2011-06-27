/* RepetitionsContainer class - has an associative array field*/

function RepetitionsContainer() {
    this.value = {};
    this.POS = {};
    this.isHighlighted = {};
}

RepetitionsContainer.prototype.add = function (key, occurrences) {
    this.value[key] = occurrences;
}

RepetitionsContainer.prototype.addPOS = function (key, pos) {
    this.POS[key] = pos;	
}

RepetitionsContainer.prototype.setIsHighlighted = function (key, isRepetitionHighlighted) {
    this.isHighlighted[key] = isRepetitionHighlighted;	
}

Array.prototype.clean = function (deleteValues) {
    for (var i = 0; i < this.length; i++) {
        if (this[i] in deleteValues.objectConverter()) {
            this.splice(i, 1);
            i--;
        }
    }
    return this;
};

Array.prototype.objectConverter = function () {
    var obj = {};
    
	for (var i = 0; i < this.length; i++) {
    	obj[this[i]] = '';
  	}

  	return obj;
};

function getKeyTerms(plain_text, html_text) {
    var repetitions = getRepetitions(plain_text);
    filterByJustesonKatzPOSRegex(repetitions);
    getHighlightedExpressions(html_text, repetitions);
    
    return repetitions;
}

function removeSpecialCharacters(text) {
	return text.replace(/[^a-z\s]/gi,"");
}

function getRepetitions(text) {
    var tokens = removeSpecialCharacters(text).split(/[\s]+/g).clean([""]);
    
    var repetitions = new RepetitionsContainer(); //associative array holding (key, value) pairs, where key is the identified string and value is the number of occurrences
	var n = tokens.length;
	var jump = 1;

    for (var k = 0; k < n - 1; k += jump) {
        jump = getRepetitionsForSentences(text, tokens, k, repetitions);
    }

    return repetitions;
}

function getRepetitionsForSentences(text, tokens, k, repetitions) {
    var n = Math.min(tokens.length-k, 4);
	var options = "gi";
	var occurrences = 0;

    for (var i = n; i >= 2; i--) {
		var colocation = tokens.slice(k, k+i).join(" ");
			
		if (colocation in repetitions.value) {
			return i;			
		}            
			
		var searchExpression = new RegExp(colocation, options);
		var matches = text.match(searchExpression);
			
   		if (matches == null) {
			continue;	
		}
		
   		occurrences = matches.length;
   		
		if (occurrences > 1) {
            repetitions.add(colocation.toLowerCase(), occurrences);
			return i;
		}
    }
	
	return 1;
}

function normalizeTag(tag) {
    if (tag == "NN" ||
        tag == "NNP" ||
        tag == "NNPS" ||
        tag == "NNS") {

        return "N";
    }

    if (tag == "JJ" ||
        tag == "JJR" ||
        tag == "JJS" ||
		tag == "VBG") {

        return "A";
    }

    return "X";
}

function getNormalizedTagExpression(taggedWords) {
    var normalizedTag = "";
	
	for (var i = 0; i < taggedWords.length; i++) {
        var taggedWord = taggedWords[i];
        var word = taggedWord[0];
        var tag = taggedWord[1];

        normalizedTag += normalizeTag(tag);
    }
	return normalizedTag;
}

function extractPartsOfSpeech(taggedWords, repetitions) {
	
	for (var i = 0; i < taggedWords.length; i++) {
        var taggedWord = taggedWords[i];
        var word = taggedWord[0];
        var tag = taggedWord[1];

        repetitions.addPOS(word, normalizeTag(tag).toLowerCase());
    }
}

function filterByJustesonKatzPOSRegex(repetitions) {
    var tagger = new POSTagger();
    var JustesonKatzRegex = new RegExp(/^((A|N)+|((A|N)*(NP)?)(A|N)*)N$/);
    var keysMarkedForRemoval = [];

    for (var key in repetitions.value) {
        var text = key.split(/[\s]+/);
        var taggedWords = tagger.tag(text);
        var normalizedTag = getNormalizedTagExpression(taggedWords);        

        if (!JustesonKatzRegex.test(normalizedTag)) {
            keysMarkedForRemoval.push(key);
        } else {
        	extractPartsOfSpeech(taggedWords, repetitions);
        }
    }

    for (var i in keysMarkedForRemoval) {
        delete repetitions.value[keysMarkedForRemoval[i]];
    }
}

function getHighlightedExpressions(text, repetitions) {
	var highlightedParagraphs = getHighlightedTextParagraphs(text);
	
	for (expression in repetitions.value) {
		repetitions.setIsHighlighted(expression, isExpressionHighlighted(expression, highlightedParagraphs));
	}
}

function isExpressionHighlighted(expression, highlightedParagraphList) {
	if (highlightedParagraphList == null) {
		return false;
	}
	
	var expressionFindingRegex = new RegExp(expression, "gi");
	
	for (var i = 0; i < highlightedParagraphList.length; i++) {
		if (expressionFindingRegex.test(highlightedParagraphList[i])) {
			return true;
		}
	}
	return false;
}

function getHighlightedTextParagraphs(text) {
	var highlightedTextFinder = new RegExp(/<h([1-6])>(.+?)<\/h[1-6]>|<b>(.+?)<\/b>|<i>(.+?)<\/i>/gi);
	
	return text.match(highlightedTextFinder);
}
