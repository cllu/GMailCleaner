/*global angular*/

angular.module('app')
  .constant('FILTERS', [
    {
      label: 'TED',
      value: 'from:(This week on TED.com <no_reply@ted.com>)',
      enabled: true
    }, {
      label: 'Hacker Newsletter',
      value: 'from:kale@hackernewsletter.com subject:(Hacker Newsletter) ',
      enabled: true
    }, {
      label: 'Spotify',
      value: 'from:no-reply@news.spotifymail.com subject:(now available on Spotify)',
      enabled: true
    }, {
      label: 'Quora',
      value: 'from:(Quora Digest <digest-noreply@quora.com>)',
      enabled: true
    }, {
      label: 'LinkedIn',
      value: 'from:messages-noreply@linkedin.com',
      enabled: true
    }, {
      label: 'Meetup',
      value: 'from:info@meetup.com subject:(Meetups this week) OR subject:(New Meetup Group)',
      enabled: true
    }, {
      label: 'Aboutme',
      value: 'from:(about.me weekly <aboutme@about.me>)',
      description: 'Aboutme Weekly',
      enabled: true
    }, {
      label: 'CrunchBase Daily',
      value: 'from:newsletter@crunchbase.com subject:(CrunchBase Daily)',
      enabled: true
    }
  ]);