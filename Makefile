tfrecord:
	python make_tfrecord.py --output_path=train.record

tweet:
	python tweet_it_od.py

plot_tweet:
	python tweet_counts.py
