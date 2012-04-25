#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Riccardo Tasso (http://github.com/raymanrt)
# License: GPL
# Bindings for the language APIs offered by Wilson Wong (http://www.wilsonwong.me/).
# For further documentation and more, please visit: http://research.wilsonwong.me/lanes.html
from requests import get

from lxml import etree


class DistributionalSimilarity:
	
	def __init__(self, *terms):
		req = 'http://research.wilsonwong.me:8080/ai/servlet/DistributionalSimilarity?t='
		
		self.sim = {}
		
		for term in terms:
			req += '[%s]' % term
		
		resp = get(req)
		if resp.ok:
			xml_resp = resp.text.encode('utf-8')
			
			root = etree.fromstring(xml_resp)
			
			# 1
			pwc = root.find('pairwisecomparison')
			for pws in pwc.findall('pairwisesim'):
				first = pws[0].text
				second = pws[1].text
				similarity = float(pws[2].text)
				
				self.set_sim(first, second, similarity)
			
			# 2
			gsim = root.find('groupavesim').text
			gsim = float(gsim)
			self.group_sim = gsim
			
			# 3
			self.outliers = []
			outliers_tag = root.find('outliers').text
			if outliers_tag:
				outliers = outliers_tag.split(', ')
				self.outliers += outliers
		
	def set_sim(self, t1, t2, v):
		if t1 > t2:
			t1, t2 = t2, t1
		
		if not t1 in self.sim:
			self.sim[t1] = {}
		
		self.sim[t1][t2] = v
	
	def get_sim(self, t1, t2):
		if t1 == t2:
			return 1
		
		if t1 > t2:
			t1, t2 = t2, t1
		
		return self.sim[t1][t2]

class ContentBearingness:
	
	def __init__(self, *terms):
		req = 'http://research.wilsonwong.me:8080/ai/servlet/ContentBearingness?t='
		
		for i, term in enumerate(terms):
			req += '[%d:%s]' % (i + 1, term)
	
		resp = get(req)
		if resp.ok:
			xml_resp = resp.text.encode('utf-8')
			
			root = etree.fromstring(xml_resp)
			
			self.contentbearingness = []
			for cb in root.findall('contentbearingness'):
				cur = {
				'rank': int(cb[0].text),
				'order': int(cb[1].text),
				'phrase': cb[2].text,
				'poisson_dev': float(cb[3].text)
				}
				
				self.contentbearingness.append(cur)

class StringSimilarity:
	
	def __init__(self, s1, s2):
		req = 'http://research.wilsonwong.me:8080/ai/servlet/StringSimilarity?s1=%s&s2=%s' % (s1, s2)
		
		resp = get(req)
		if resp.ok:
			xml_resp = resp.text.encode('utf-8')
			
			root = etree.fromstring(xml_resp)
			
			strsim = root.find('strsim').text
			self.sim = float(strsim)

class InputInterpreter:
	def __init__(self, q, ws):
		req = 'http://research.wilsonwong.me:8080/ai/servlet/InputInterpreter?q=%s&ws=%s' % (q, ws)
		
		if ws not in ['poisson', 'tfidf', 'noweight']:
			raise Exception('invalid ws!')
		
		resp = get(req)
		if resp.ok:
			xml_resp = resp.text.encode('utf-8')
			
			root = etree.fromstring(xml_resp)
			
			# 1
			self.input = root.find('input').text
			
			# 2
			analysis = root.find('sentence-analysis')
			self.analysis = {
			'sentiment': float(analysis.find('sentiment').text),
			'affirmation': float(analysis.find('affirmation').text),
			'greeting': float(analysis.find('greeting').text),
			'question': float(analysis.find('question').text),
			'exe_time': int(analysis.find('error').find('text').text),
			}
			
			# 3
			parsing = root.find('sentence-parsing')
			parsed_input_n = parsing.find('parsedinput')
			
			parsed_input = []
			for tagged_word in parsed_input_n.findall('taggedword'):
				tagged_word = {
				'offset': int(tagged_word.find('offset').text),
				'word': tagged_word.find('word').text,
				'tag': tagged_word.find('tag').text,
				}
				
				parsed_input.append(tagged_word)
				
			self.sentence_parsing = {
			'parsed_input': parsed_input,
			'exe_time': int(parsing.find('error').find('text').text),
			}
			
			# 4
			extraction = root.find('phrase-extraction')
			
			phrase = []
			for token in extraction.findall('phrase'):
				
				t_type = token.find('type').text
				if t_type == 'NULL':
					t_type = None

				topic = token.find('topic').text
				if topic:
					topic = topic[1:-1] # TODO: can have multi-topic?

				phrase_cur = {
				'ngram': token.find('ngram').text,
				'type': t_type,
				'topic': topic,
				}

				phrase.append(phrase_cur)

			self.phrase_extraction = {
			'phrase': phrase,
			'exe_time': int(extraction.find('error').find('text').text),
			}

			# 5
			keyphrase = root.find('keyphrase-analysis')

			phrase = []
			for token in keyphrase.findall('keyphrase'):
				
				phrase_cur = {
				'phrase': token.find('phrase').text,
				'weight': float(token.find('weight').text),
				}

				phrase.append(phrase_cur)

			self.keyphrase_analysis = {
			'phrase': phrase,
			'exe_time': int(keyphrase.find('error').find('text').text),
			}			
			
			
		# TODO: long

class CorpusStatistics:
	def __init__(self, term):
		req = 'http://research.wilsonwong.me:8080/ai/servlet/CorpusStatistics?t=%s' % term
			
		resp = get(req)
		if resp.ok:
			xml_resp = resp.text.encode('utf-8')
			
			root = etree.fromstring(xml_resp)
			
			metadata = root.find('metadata')
			self.metadata = {
			'total_docs': metadata.find('totaldocincollection').text,
			'total_docs_containing_term': metadata.find('totaldoccontainingterm').text,
			'total_occurrences_in_collection': metadata.find('totaloccurrencesincollection').text,
			}
			
			self.articles = []
			for article in root.find('articles'):
				id = article.find('id').text
				occurrence = article.find('occurrence').text
				
				self.articles.append({
					'id': int(id),
					'occurrence': int(occurrence),
				})
